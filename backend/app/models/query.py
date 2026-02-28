from db.models.query import Query
from sqlalchemy.orm import Session


class QueryModel:

    def __init__(self, db: Session):
        self.db = db

    def create_query(self, query, response, user_id):
        query = Query(
            query=query,
            reponse=response,
            user_id=user_id,
        )

        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)

        return query

    def get_user_queries(self, user_id):
        queries = self.db.query(Query).filter(Query.user_id == user_id).all()
        return queries
