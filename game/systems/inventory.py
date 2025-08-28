"""
Inventory System for Rent Quest
Manages player items, weapons, and equipment
"""

from typing import Dict, List, Optional, Any
from enum import Enum

class ItemType(Enum):
    """Types of items in the game"""
    WEAPON = "weapon"
    CONSUMABLE = "consumable"
    UPGRADE = "upgrade"
    QUEST_ITEM = "quest_item"

class Item:
    """Base item class"""
    
    def __init__(self, name: str, item_type: ItemType, description: str = "", 
                 value: int = 0, stackable: bool = False, max_stack: int = 1):
        """Initialize item"""
        self.name = name
        self.item_type = item_type
        self.description = description
        self.value = value  # Sell price
        self.stackable = stackable
        self.max_stack = max_stack
        
    def __str__(self):
        return self.name

class InventorySlot:
    """Represents a single inventory slot"""
    
    def __init__(self, item: Optional[Item] = None, quantity: int = 0):
        """Initialize inventory slot"""
        self.item = item
        self.quantity = quantity
        
    def is_empty(self) -> bool:
        """Check if slot is empty"""
        return self.item is None or self.quantity <= 0
        
    def can_add(self, item: Item, quantity: int = 1) -> bool:
        """Check if item can be added to this slot"""
        if self.is_empty():
            return True
        if self.item.name == item.name and item.stackable:
            return self.quantity + quantity <= item.max_stack
        return False
        
    def add_item(self, item: Item, quantity: int = 1) -> int:
        """Add item to slot, returns quantity actually added"""
        if self.is_empty():
            self.item = item
            self.quantity = min(quantity, item.max_stack if item.stackable else 1)
            return self.quantity
        elif self.item.name == item.name and item.stackable:
            max_add = min(quantity, item.max_stack - self.quantity)
            self.quantity += max_add
            return max_add
        return 0
        
    def remove_item(self, quantity: int = 1) -> int:
        """Remove item from slot, returns quantity actually removed"""
        if self.is_empty():
            return 0
        removed = min(quantity, self.quantity)
        self.quantity -= removed
        if self.quantity <= 0:
            self.item = None
            self.quantity = 0
        return removed

class Inventory:
    """Player inventory system"""
    
    def __init__(self, size: int = 30):
        """Initialize inventory"""
        self.size = size
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(size)]
        
    def add_item(self, item: Item, quantity: int = 1) -> int:
        """Add item to inventory, returns quantity actually added"""
        remaining = quantity
        
        # First, try to add to existing stacks
        if item.stackable:
            for slot in self.slots:
                if not slot.is_empty() and slot.item.name == item.name:
                    added = slot.add_item(item, remaining)
                    remaining -= added
                    if remaining <= 0:
                        break
                        
        # Then, try to add to empty slots
        if remaining > 0:
            for slot in self.slots:
                if slot.is_empty():
                    added = slot.add_item(item, remaining)
                    remaining -= added
                    if remaining <= 0:
                        break
                        
        return quantity - remaining
        
    def remove_item(self, item_name: str, quantity: int = 1) -> int:
        """Remove item from inventory, returns quantity actually removed"""
        removed = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.name == item_name:
                slot_removed = slot.remove_item(quantity - removed)
                removed += slot_removed
                if removed >= quantity:
                    break
        return removed
        
    def has_item(self, item_name: str, quantity: int = 1) -> bool:
        """Check if inventory has specified quantity of item"""
        total = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.name == item_name:
                total += slot.quantity
                if total >= quantity:
                    return True
        return False
        
    def get_item_count(self, item_name: str) -> int:
        """Get total count of specified item"""
        total = 0
        for slot in self.slots:
            if not slot.is_empty() and slot.item.name == item_name:
                total += slot.quantity
        return total
        
    def get_items_by_type(self, item_type: ItemType) -> List[InventorySlot]:
        """Get all items of specified type"""
        items = []
        for slot in self.slots:
            if not slot.is_empty() and slot.item.item_type == item_type:
                items.append(slot)
        return items
        
    def is_full(self) -> bool:
        """Check if inventory is full"""
        return all(not slot.is_empty() for slot in self.slots)
        
    def get_empty_slots(self) -> int:
        """Get number of empty slots"""
        return sum(1 for slot in self.slots if slot.is_empty())
        
    def clear(self):
        """Clear all items from inventory"""
        for slot in self.slots:
            slot.item = None
            slot.quantity = 0