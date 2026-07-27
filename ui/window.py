class Window:
    def __init__(self):
        self.children=[]

    def add(self,widget):
        self.children.append(widget)

    def draw(self,display):
        for item in self.children:
            item.draw(display)