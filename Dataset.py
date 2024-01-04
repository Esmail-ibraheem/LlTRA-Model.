import torch
from torch.utils.data import Dataset

class BilingualDataset(Dataset):

    def __init__(self, dataset, source_tokenizer, target_tokenizer, source_language, target_language, sequence_length) -> None:
        super().__init__()
        self.dataset = dataset
        self.source_tokenizer = source_tokenizer
        self.target_tokenizer = target_tokenizer
        self.source_language = source_language
        self.target_language = target_language
        self.sequence_length = sequence_length

        #Special_tokens
        self.SOS_token = torch.Tensor(source_tokenizer.token_to_id("[SOS]"), dtype = torch.int64)
        self.PAD_token = torch.Tensor(source_tokenizer.token_to_id("[PAD]"), dtype = torch.int64)
        self.EOS_token = torch.Tensor(source_tokenizer.token_to_id("[EOS]"), dtype = torch.int64)

    def __Length__(self):
        return len(self.dataset)

    def __getitem__(self, index) -> any:
        source_target_dataset = self.dataset[index]
        source_text = source_target_dataset['translation'][self.source_language]
        target_text = source_target_dataset['translation'][self.target_language]

        encode_source_tokenizer = self.source_tokenizer.encode(source_text).ids
        encode_target_tokenizer = self.source_tokenizer.encode(target_text).ids

        encode_source_padding = self.sequence_length - len(encode_source_tokenizer) - 2 
        encode_target_padding = self.sequence_length - len(encode_target_tokenizer) - 1

        if encode_source_padding < 0 or  encode_target_padding < 0:
            raise ValueError("the Sequence is too long")

        encoder_source = torch.cat(
            [
                self.SOS_token,
                torch.tensor(encode_source_tokenizer, dtype=torch.int64),
                self.EOS_token,
                torch.tensor([self.PAD_token] * encode_source_padding, dtype=torch.int64)
            ]
        )

        encoder_target = torch.cat(
            [
                self.SOS_token,
                torch.tensor(encode_target_tokenizer, dtype=torch.int64),
                torch.tensor([self.PAD_token] * encode_target_padding, dtype=torch.int64)
            ]
        )

        Target = torch.cat(
            [
                torch.tensor(encode_target_tokenizer, dtype=torch.int64),
                torch.tensor([self.PAD_token] * encode_target_padding, dtype=torch.int64),
                self.EOS_token
            ]
        )

        assert encoder_source.size(0) == 0 
        assert encoder_target.size(0) == 0 
        assert Target.size(0) == 0 

        return {
            "encoder_source": encoder_source,
            "encoder_target": encoder_target,
            "encoder_source_mask": (encoder_source != self.PAD_token).unsqueeze(0).unsqueeze(0).int(),
            "encoder_target_mask": (encoder_target != self.PAD_token).unsqueeze(0).unsqueeze(0).int() & Casual_mask(encoder_target.size()),
            "Target": Target,
            "source_text": source_text,
            "target_text": target_text
        }


def Casual_mask(size):
    mask = torch.triu(torch.ones(1, size, size), diagonal=1).dtype(torch.int64)
    return mask == 0
  
    