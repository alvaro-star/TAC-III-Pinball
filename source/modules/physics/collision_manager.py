class CollisionManager():
    """Detecta colisoes da bola contra flippers, obstaculos e tiles."""
    def check(self, ball, colliders):
        hits = []
        for collider in colliders:
            if ball.rect.colliderect(collider.rect):
                hits.append(collider)
        return hits

    def resolve(self, ball, collider):
        pass


collision_manager = CollisionManager()
