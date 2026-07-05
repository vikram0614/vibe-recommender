import laion_clap
import numpy as np

model = laion_clap.CLAP_Module(enable_fusion=False)
model.load_ckpt()  # downloads pretrained checkpoint automatically, first run only

def embed_audio(filepath):
    audio_embed = model.get_audio_embedding_from_filelist(x=[filepath], use_tensor=False)
    return audio_embed[0]  # numpy array