import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments
import os

class CodeGPT:
    def __init__(self, model_name='gpt2', output_dir='./code_gpt_model'):
        self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
        self.model = GPT2LMHeadModel.from_pretrained(model_name)
        self.output_dir = output_dir

        # Add special tokens for code
        special_tokens = {'pad_token': '<PAD>', 'bos_token': '<START>', 'eos_token': '<END>'}
        num_added_toks = self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def prepare_dataset(self, file_path, block_size=128):
        dataset = TextDataset(
            tokenizer=self.tokenizer,
            file_path=file_path,
            block_size=block_size,
        )
        return dataset

    def train(self, train_file, eval_file=None, epochs=5, batch_size=4):
        train_dataset = self.prepare_dataset(train_file)
        eval_dataset = self.prepare_dataset(eval_file) if eval_file else None

        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer, mlm=False
        )

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            overwrite_output_dir=True,
            num_train_epochs=epochs,
            per_device_train_batch_size=batch_size,
            save_steps=10_000,
            save_total_limit=2,
            evaluation_strategy="epoch" if eval_dataset else "no",
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            data_collator=data_collator,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
        )

        trainer.train()
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

    def generate_code(self, prompt, max_length=100):
        input_ids = self.tokenizer.encode(prompt, return_tensors='pt')
        attention_mask = torch.ones(input_ids.shape, dtype=torch.long)
        pad_token_id = self.tokenizer.pad_token_id

        output = self.model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_length=max_length,
            num_return_sequences=1,
            no_repeat_ngram_size=2,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=pad_token_id,
            bos_token_id=self.tokenizer.bos_token_id,
            eos_token_id=self.tokenizer.eos_token_id,
        )

        generated_code = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return generated_code

# Usage example
if __name__ == "__main__":
    code_gpt = CodeGPT()

    # Assuming you have a file with code examples
    train_file = "path_to_your_code_dataset.txt"
    
    # Train the model
    code_gpt.train(train_file, epochs=3, batch_size=4)

    # Generate code
    prompt = "def fibonacci(n):"
    generated_code = code_gpt.generate_code(prompt)
    print(f"Generated code:\n{generated_code}")
