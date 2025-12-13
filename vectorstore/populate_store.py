from faiss_store import VectorStore

store = VectorStore()

store.add_consult_type("consulta de rotina", synonyms=["rotina", "padrao"])
store.add_consult_type("vacinação", synonyms=["vacina"])
store.add_consult_type("urgência", synonyms=["urgente", "emergência"])
store.add_consult_type("consulta médica", synonyms=["consulta", "medica"])

print("Vector store FAISS populada.")