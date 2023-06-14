import wandb
import os
from official.nlp import optimization
import tensorflow as tf
import nltk
from lime.lime_text import LimeTextExplainer
import numpy as np

class Trainer():
    def __init__(self, config, model, dataset, name) -> None:
        self.config = config
        self.model = model
        self.dataset = dataset
        self.name = name
        self.get_dataset_partitions_tf(dataset, config["datasize"])
        self.init_wandb()

    def init_wandb(self):
        wandb.init(
            project="news-fuse",
            config=self.config,
            settings=wandb.Settings(code_dir="..."),
            name = self.name,
        )
        wandb.log(self.config)

        
    def get_dataset_partitions_tf(self, ds, ds_size, train_split=0.9, val_split=0.05, test_split=0.05):
        assert (train_split + test_split + val_split) == 1
        
        train_size = int(train_split * ds_size)
        val_size = int(val_split * ds_size)
        
        self.train_ds = ds.take(train_size).batch(self.config["batch_size"])
        self.val_ds = ds.skip(train_size).take(val_size).batch(self.config["batch_size"])
        self.test_ds = ds.skip(train_size).skip(val_size).batch(self.config["batch_size"])
        

    def compile_model(self):
        optimizer = optimization.create_optimizer(
            init_lr=self.config["init_lr"],
            num_train_steps=self.config["num_train_steps"],    
            num_warmup_steps=self.config["num_warmup_steps"],
            optimizer_type='adamw'
        )
        loss = tf.keras.losses.BinaryCrossentropy()
        metrics = tf.metrics.BinaryAccuracy()

        self.model.compile(
            optimizer=optimizer,
            loss=loss,  
            metrics=metrics
        )

    def train(self):
        history = self.model.fit(
            x=self.train_ds,
            epochs=self.config["epochs"],
            validation_data=self.val_ds,
            callbacks=[wandb.keras.WandbCallback(save_model = False)]
        )

    def test_model(self):
        test_data = self.model.evaluate(self.test_ds)
        wandb.log({"test loss": test_data[0],
                   "test binary_accuracy": test_data[1]})
        return test_data
    
    def predict_model(self, text, label, log = True):
        prediction = self.model.predict([text])
        if log:
            wandb.log({label: text, "model_prediction": prediction})
        return prediction

    def save_model(self):
        self.model.save(os.path.join(wandb.run.dir, "model.h5"))

    def get_probabilities(self, text):
        prob = self.model.predict([text])
        return np.hstack([1 - prob, prob])

    def explain_prediction(self, text, label, log = True):
        explainer = LimeTextExplainer(class_names=["Non-biased", "Biased"])
        with tf.device("/cpu:0"):
            explanation = explainer.explain_instance(text, self.get_probabilities, num_features=10)
            if log:
                data = [[label, val] for (label, val) in explanation.as_list()]
                table = wandb.Table(data=data, columns = ["label", "value"])
                wandb.log({label : wandb.plot.bar(table, "label", "value", title=label)})
            return explanation

