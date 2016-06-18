from spInDP.Behavior import Behavior

class DanceBehavior(Behavior):

    Started = False

    def __init__(self,spider):
        super(DanceBehavior,self).__init__(spider)

    def update(self):
        if(self.Started):
            #1. Strekken
            #2. Buiging
            #3. Sierlijk Stafen
            #4. Pirouette
            #5. Op spitsen lopen
            #6. 'Molen' met voorste armen
            #7. Twerken
            #8. Trippelen
            #9. Draaien op 4 poten, 2 middlste poten uitgestrekt
            #10. Foxtrot-basis
            #11. Paardrijden (gangnam move)
            #12. Moonwalk
            #13. De travolta
            #14. Hammer time

            self.spider.sequenceController.parseSequence("sequences/startup.txt")

    def startMusic(self):
        self.Started = True