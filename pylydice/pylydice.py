import argparse
import random
import re
from dataclasses import dataclass
from enum import Enum

DICE_DEFN_PATTERN = "(\\d*)d(\\d*)([+|-]?\\d*)"

# FIXME: change to best-n and worst-n


class RollType(Enum):
    """Defines the type of roll being made."""

    NORMAL = 1
    ADVANTAGE = 2
    DISADVANTAGE = 3

    def __str__(self):
        return self.name.lower()


@dataclass
class RollDefinition:
    """Defines a roll specification."""

    num_rolls: int
    die: int
    modifier: int
    type: RollType

    @property
    def defn(self):
        """Generates the formatted string representation of the roll definition."""
        mod = ""
        if self.modifier > 0:
            mod = f"+{self.modifier}"
        elif self.modifier < 0:
            mod = f"{self.modifier}"

        return f"{self.num_rolls if self.num_rolls > 1 else ''}d{self.die}{mod}"


@dataclass
class RollResults:
    """The results of a roll."""

    roll_defn: RollDefinition
    rolls: [int]

    @property
    def total(self):
        """The total value of the resulting rolls (including modifier)."""
        total = 0
        for _r in self.rolls:
            total += _r

        total += self.roll_defn.modifier
        return total

    def __lt__(self, other):
        return self.total < other.total


def main():
    """Entry point to the application."""
    parser = argparse.ArgumentParser(description="Roll some dice.")
    parser.add_argument(
        "-a", "--advantage", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "-d", "--disadvantage", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument("roll_defn")

    args = parser.parse_args()

    modifier = RollType.NORMAL
    if args.advantage:
        modifier = RollType.ADVANTAGE
    elif args.disadvantage:
        modifier = RollType.DISADVANTAGE

    rolled = roll(args.roll_defn, modifier)
    roll_mod = (
        rolled.roll_defn.modifier
        if rolled.roll_defn.modifier < 0
        else f"+{rolled.roll_defn.modifier}"
    )

    print(
        f"""\
Rolling {rolled.roll_defn.defn} ({rolled.roll_defn.type})
Rolled {rolled.rolls} ({roll_mod})
Got {rolled.total}
    """
    )


def roll(dice_defn_str, roll_type) -> RollResults:
    """Rolls the dice based on the supplied definition and roll type."""
    _m = re.compile(DICE_DEFN_PATTERN).match(dice_defn_str)

    roll_def = RollDefinition(
        int(_m.group(1)) if _m.group(1) else 1,
        int(_m.group(2)),
        int(_m.group(3)) if _m.group(3) else 0,
        roll_type,
    )

    if roll_type == RollType.DISADVANTAGE:
        roll_1 = _roll_dice(roll_def)
        roll_2 = _roll_dice(roll_def)
        return min(roll_1, roll_2)

    elif roll_type == RollType.ADVANTAGE:
        roll_1 = _roll_dice(roll_def)
        roll_2 = _roll_dice(roll_def)
        return max(roll_1, roll_2)

    else:
        return _roll_dice(roll_def)


def _roll_dice(dice_defn) -> RollResults:
    result = RollResults(dice_defn, [])

    for _ in range(0, dice_defn.num_rolls):
        result.rolls.append(random.randint(1, dice_defn.die))

    return result
