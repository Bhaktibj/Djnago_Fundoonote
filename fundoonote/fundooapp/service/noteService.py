from models import Notes
class NoteService:
    def __init__(self, note_id=False):
        if self:
            pass
    def getNote(self):
        if not self._id:
            raise Exception('Unable to find the note')
        else:
            Notes.objects.get(pk=self._id)

    def addNote(self):
        pass

    def pin(self):
        pass

    def unpin(self):
        pass

    def archive(self):
        pass

    def remainder(self):
        pass

    def trash(self):
        pass

    def color(self):
        pass

    def addLabel(self):
        pass