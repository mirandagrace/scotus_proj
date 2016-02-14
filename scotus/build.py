from .db.models import BuildStatus 

class Build:
  def __init__(self):
    self.phases = {}

  def run(self, session):
    phases = self.build_order()
    for phase in phases:
      phase(session)
    return

  def build_order(self):
    transaction_list = [p for p in self.phases.values()]
    transaction_list.sort(key = lambda x: x.precidence)
    return transaction_list
  
  def add(self, precidence, transaction, name=None):
    phase = Phase(precidence, transaction, name=name)
    if phase.name in self.phases:
      raise ValueError, "Name already in use."
    else:
      
      self.phases[phase.name] = phase
      return phase

class Phase:
  def __init__(self, precidence, transaction, name=None):
    self.precidence = precidence
    self.transaction = transaction
    if name != None:
      self.name = name
    else:
      self.name =  transaction.__name__   
    
  def __call__(self, session):
    try:
      status_query = session.query(BuildStatus).filter(BuildStatus.name == self.name).all()
      if len(status_query) == 0: 
        status = BuildStatus(name=self.name, complete=False)
        session.add(status)
      elif len(status_query) == 1: 
        status = status_query[0]
      else:  # pragma: no cover
        status_query.one()

      if not status.complete:
        self.transaction(session)
        status.complete = True
      session.commit()
    except:
      session.rollback()
      raise
    return
    
