from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# Configuração CORS (Permitir que o frontend fale com o backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexão Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Modelos de Dados
class PedidoCreate(BaseModel):
    medicamentos: List[str]

class PedidoUpdate(BaseModel):
    status: str

@app.get("/api/health")
def health():
    return {"status": "online", "backend": "vercel-python"}

@app.post("/api/pedidos")
def criar_pedido(pedido: PedidoCreate):
    senha = f"F{random.randint(100, 999)}"
    
    data = {
        "senha": senha,
        "medicamentos": pedido.medicamentos,
        "status": "pendente"
    }
    
    response = supabase.table("pedidos").insert(data).execute()
    
    # Tratamento de resposta do Supabase (pode variar conforme a versão da lib)
    if not response.data:
         raise HTTPException(status_code=500, detail="Erro ao salvar no banco")
         
    return response.data[0]

@app.get("/api/pedidos")
def listar_pedidos():
    # Pega os últimos 50 pedidos, ordenados pelo mais recente
    response = supabase.table("pedidos").select("*").order("created_at", desc=True).limit(50).execute()
    return response.data

@app.patch("/api/pedidos/{pedido_id}")
def atualizar_status(pedido_id: int, update: PedidoUpdate):
    response = supabase.table("pedidos").update({"status": update.status}).eq("id", pedido_id).execute()
    return response.data
