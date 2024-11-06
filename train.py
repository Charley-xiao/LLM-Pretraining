import argparse
import yaml
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from transformers.trainer_utils import get_last_checkpoint
import torch
from torch.utils.data import DataLoader
from transformers import DataCollatorForLanguageModeling

argparser = argparse.ArgumentParser()
argparser.add_argument("--config", type=str, default="cfg/train.yaml", help="Path to the configuration file")
argparser.add_argument("--local_rank", type=int, default=-1, help="Local rank for distributed training")
args = argparser.parse_args()

def load_config(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

def main():
    config = load_config(args.config)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    tokenizer = AutoTokenizer.from_pretrained(config['model_name'])
    model = AutoModelForCausalLM.from_pretrained(config['model_name'])
    tokenizer.pad_token = tokenizer.eos_token

    dataset = load_dataset("json", data_files=config['dataset'])
    
    def tokenize_function(examples):
        return tokenizer(examples['content'], truncation=True, padding='max_length', max_length=config['max_length'])

    tokenized_datasets = dataset.map(tokenize_function, batched=True)

    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False, 
    )

    training_args = TrainingArguments(
        output_dir=config['output_dir'],
        per_device_train_batch_size=config['batch_size'],
        eval_strategy="epoch",
        logging_dir=config['logging_dir'],
        learning_rate=config['learning_rate'],
        num_train_epochs=config['epochs'],
        save_strategy="epoch",
        save_total_limit=2,
        logging_steps=10,
        load_best_model_at_end=True,
        ddp_find_unused_parameters=False, 
        report_to="none", 
        gradient_accumulation_steps=config['grad_accumulation_steps'], 
        fp16=True,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_datasets['train'],
        eval_dataset=tokenized_datasets['train'], # TODO: Change to eval dataset!!
        tokenizer=tokenizer,
        data_collator=data_collator,
    )

    trainer.train(resume_from_checkpoint=get_last_checkpoint(config['output_dir']))

if __name__ == '__main__':
    main()

# torchrun --nproc_per_node=NUM_GPUS train.py
