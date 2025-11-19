
class Registry () : 

    """
    cette classe implemente le fonctionnement du design pattern registre , c'est un constructeur 

    """

    def __init__(self):
        self.register={}

    def is_valid_request (self): 
        pass 
        
    def __call__(self,name):
        def decorator (obj) : 
            self.register[name]=obj
            return obj
        return decorator
    
    def __str__(self) : 
        return str(self.register)
    
    def get(self,name) : 
        return self.register[name]
    
        