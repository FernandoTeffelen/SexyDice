from app import create_app, db
from app.models import User

# Cria uma instância da aplicação para ter acesso ao contexto do banco de dados
app = create_app()

# O código abaixo só será executado dentro do contexto da aplicação
with app.app_context():
    # --- Coloque os IDs dos usuários que você quer deletar aqui ---
    ids_para_deletar = [2, 3]

    try:
        # Busca todos os usuários com os IDs da lista
        usuarios_para_deletar = User.query.filter(User.id.in_(ids_para_deletar)).all()

        if not usuarios_para_deletar:
            print(f"Nenhum usuário encontrado com os IDs: {ids_para_deletar}")
        else:
            for user in usuarios_para_deletar:
                print(f"Deletando usuário: ID={user.id}, Email={user.email}...")
                # O SQLAlchemy vai cuidar de deletar em cascata as assinaturas e pagamentos
                db.session.delete(user)
            
            # Confirma a transação, efetivamente deletando os dados do banco
            db.session.commit()
            print("\nUsuários deletados com sucesso!")

    except Exception as e:
        # Em caso de erro, desfaz qualquer mudança
        db.session.rollback()
        print(f"\nOcorreu um erro: {e}")
