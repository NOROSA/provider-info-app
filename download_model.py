from transformers import AutoModel, AutoTokenizer

# Nombre del modelo a descargar
model_name = "distilbert-base-multilingual-cased"

# Descargar y guardar el modelo y el tokenizer localmente
print("Descargando modelo...")
AutoModel.from_pretrained(model_name).save_pretrained("./models/distilbert")
AutoTokenizer.from_pretrained(model_name).save_pretrained("./models/distilbert")
print("Modelo descargado y guardado en ./models/distilbert")