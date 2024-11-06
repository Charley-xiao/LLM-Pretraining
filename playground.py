import argparse
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

argparser = argparse.ArgumentParser()
argparser.add_argument("--model_name", type=str, default="gpt2", help="Model name")
args = argparser.parse_args()

def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    tokenizer = AutoTokenizer.from_pretrained(args.model_name)
    model = AutoModelForCausalLM.from_pretrained(args.model_name).to(device)
    tokenizer.pad_token = tokenizer.eos_token

    user_input = input("Enter text to generate: ")
    user_input = user_input.strip()
    inputs = tokenizer(user_input, return_tensors="pt").input_ids.to(device)
    
    print("Possible completions (different temperatures):")
    for temperature in [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]:
        print(f"Temperature: {temperature}")
        output = model.generate(inputs, max_length=100, temperature=temperature, do_sample=True)
        print(tokenizer.decode(output[0], skip_special_tokens=True))

if __name__ == '__main__':
    main()