from __future__ import annotations 
from typing import Protocol
from dataclasses import dataclass
from required_types import PlayerId, HandId, TapVariant, WinVariant, Action, HandInfo


class TapRule(Protocol):
    def tap(self, target: HandInfo, add: int) -> HandInfo | None:
        ...

class CutoffTapRule:
    def tap(self, target: HandInfo, add: int) -> HandInfo | None:
        new_finger: int = target.fingers_up + add
        if new_finger >= 5:
            return Hand(
                hand_id=target.hand_id,
                player_id=target.player_id,
                fingers_up=0,
                total_fingers=target.total_fingers
            )
        return target.to(new_finger)

class RollOverTapRule:
    def tap(self, target: HandInfo, add: int) -> HandInfo | None:
        new_fingers = target.fingers_up + add
        if new_fingers == 5:
            return Hand(
                hand_id=target.hand_id,
                player_id=target.player_id,
                fingers_up=0,
                total_fingers=target.total_fingers
            )
        elif new_fingers > 5:
            return target.to(new_fingers-5)
        return target.to(new_fingers)

class WinRule(Protocol):
    def get_winner(self, players: dict[PlayerId, list[HandInfo]]) -> PlayerId | None:
        ...

class StandardWinRule:
    def get_winner(self, players: dict[PlayerId, list[HandInfo]]) -> PlayerId | None:
        active_players = [player for player, hands in players.items() if any(h.is_active() for h in hands)]
        if len(active_players) == 1:
            return active_players[0]
        return None

class MisereAWinRule:
    def get_winner(self, players: dict[PlayerId, list[HandInfo]]) -> PlayerId | None:
        eliminated = [player for player, hands in players.items() if all(h.is_inactive() for h in hands)]
        return eliminated[0] if eliminated else None

class MisereBWinRule:
    def get_winner(self, players: dict[PlayerId, list[HandInfo]]) -> PlayerId | None:
        active_players = [player for player, hands in players.items() if any(h.is_active() for h in hands)]
        if len(active_players) == 1:
            eliminated = [player for player, hands in players.items() if all(h.is_inactive() for h in hands)]
            return eliminated[-1] if eliminated else None
        return None

@dataclass
class Hand:    
    hand_id: HandId
    player_id: PlayerId
    fingers_up: int
    total_fingers: int = 5

    def is_active(self) -> bool:
        return (0 < self.fingers_up < self.total_fingers)

    def is_inactive(self) -> bool:
        return not self.is_active()

    def to(self, fingers_up: int) -> HandInfo | None:
        if fingers_up <= 0 or fingers_up > self.total_fingers:
            return None
        else:
            return Hand(
                hand_id=self.hand_id, 
                player_id=self.player_id, 
                fingers_up=fingers_up,
                total_fingers=self.total_fingers
            )

class ChopsticksModel:
    def __init__(self, n: int, tap_rule: TapRule, win_rule: WinRule):

        self._players : list[PlayerId] = [PlayerId(i) for i in range(1, n+1)]
        self.starting_hand: int = 1
        self._player_hands : dict[PlayerId, list[HandInfo]] = {
            player: [
                Hand(HandId(1), player, self.starting_hand), 
                Hand(HandId(2), player, self.starting_hand)
            ] 
            for player in self._players
        }
        self.tap_rule = tap_rule
        self.win_rule = win_rule
        self.current_player_index: int = 0

    @property
    def current_player_id(self) -> PlayerId:
        return self._players[self.current_player_index]

    @property
    def current_player_hands(self) -> list[HandInfo]:
        return self.get_player_hands(self.current_player_id)

    def get_player_hands(self, player_id: PlayerId) -> list[HandInfo]:
        return self._player_hands[player_id]

    def get_hands_all_players(self) -> dict[PlayerId, list[HandInfo]]: 
        return self._player_hands

    def get_winner(self) -> PlayerId | None:
        return self.win_rule.get_winner(self._player_hands)

    def get_split_sources(self) -> list[HandInfo]:
        return [h for h in self.current_player_hands if h.fingers_up>1]

    def get_split_targets(self, source: HandInfo) -> list[HandInfo]:
        return [h for h in self.current_player_hands if source.hand_id != h.hand_id]
    
    def get_tap_sources(self) -> list[HandInfo]:
        return [h for h in self.current_player_hands if h.is_active()]

    def get_tap_targets(self) -> list[HandInfo]:
        return [
            h 
            for players,hands in self.get_hands_all_players().items() 
            if players!=self.current_player_id 
            for h in hands 
            if h.is_active()
        ]
    
    def do_tap(self, source: HandId, target: tuple[PlayerId, HandId]) -> bool: 
        target_playerid, target_handid = target
        
        source_hand = self._get_hand(self.current_player_id, source)
        target_hand = self._get_hand(target_playerid, target_handid)

        if source_hand is None or not source_hand.is_active():
            return False 

        if target_hand is None or not target_hand.is_active():
            return False

        new_target = self.tap_rule.tap(target_hand, source_hand.fingers_up)
        if new_target is None:
            return False
        self._replace_hand(target_playerid, new_target)

        self.current_player_index = (self.current_player_index + 1) % len(self._players)
        return True

    def _get_hand(self, player_id: PlayerId, hand_id: HandId):
        for h in self._player_hands[player_id]:
            if h.hand_id == hand_id:
                return h
        return None

    def _replace_hand(self, player_id: PlayerId, updated_hand: HandInfo):
        hands = self._player_hands[player_id]
        for i, h in enumerate(hands):
            if h.hand_id == updated_hand.hand_id:
                hands[i] = updated_hand
                return


    def do_split(self, source: HandId, target: HandId, to_transfer: int) -> bool:
        source_hand = self._get_hand(self.current_player_id, source)
        target_hand = self._get_hand(self.current_player_id, target)

        if (
            source_hand is None or target_hand is None
            or source_hand.hand_id == target_hand.hand_id
            or to_transfer<=0
            or to_transfer >= source_hand.fingers_up
            or target_hand.fingers_up + to_transfer >= target_hand.total_fingers
        ):
            return False

        source_diff = source_hand.fingers_up - to_transfer
        target_sum = target_hand.fingers_up + to_transfer

        new_source = source_hand.to(source_diff)
        new_target = target_hand.to(target_sum)

        if new_source is None or new_target is None:
            return False

        self._replace_hand(self.current_player_id, new_source)
        self._replace_hand(self.current_player_id, new_target)

        self.current_player_index = (self.current_player_index + 1) % len(self._players)
        return True

    
    @classmethod 
    def make(cls, n: int, tap_variant: TapVariant, win_variant: WinVariant) -> ChopsticksModel:
        match tap_variant:
            case TapVariant.CUTOFF:
                tap_rule: TapRule = CutoffTapRule()
            case TapVariant.ROLLOVER:
                tap_rule: TapRule = RollOverTapRule()
            case _:
                raise ValueError(f"No {tap_variant} found")
        match win_variant:
            case WinVariant.STANDARD:
                win_rule: WinRule = StandardWinRule()
            case WinVariant.MISERE_A:
                win_rule: WinRule = MisereAWinRule()
            case WinVariant.MISERE_B:
                win_rule: WinRule = MisereBWinRule()
            case _:
                raise ValueError(f"No {win_variant} found")

        return cls(n, tap_rule, win_rule)
