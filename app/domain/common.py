from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import UUID

class Command:
    pass

class Query:
    pass

class Event:
    pass

class CommandHandler(ABC):
    @abstractmethod
    def handle(self, command: Command):
        pass

class QueryHandler(ABC):
    @abstractmethod
    def handle(self, query: Query):
        pass

class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: Event):
        pass

class Repository(ABC):
    pass

class AggregateRoot:
    _events: List[Event] = []
    
    def add_event(self, event: Event):
        self._events.append(event)
    
    def clear_events(self):
        self._events.clear()
    
    def get_events(self) -> List[Event]:
        return self._events.copy()