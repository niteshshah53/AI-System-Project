(define (domain wumpus-world)
  (:requirements :adl :typing)
  (:types 
    location - object
    agent - object
    direction - object
  )
  
  (:predicates
    (at ?obj - object ?loc - location)
    (adjacent ?loc1 ?loc2 - location ?dir - direction)
    (has-arrow ?agent - agent)
    (has-key ?agent - agent)
    (wumpus ?loc - location)
    (wall ?loc - location)
    (crate ?loc - location)
    (trampoline ?loc - location)
    (door ?loc - location)
    (arrow ?loc - location)
    (key ?loc - location)
    (empty ?loc - location)
    (edge ?loc - location ?dir - direction)
    (free ?agent - agent)
  )

  (:action walk
    :parameters (?a - agent ?from - location ?to - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (adjacent ?from ?to ?dir)
      (not (wall ?to))
      (not (wumpus ?to))
      (not (door ?to))
      (not (crate ?to))
      (or (empty ?to) (arrow ?to) (key ?to) (trampoline ?to))
      (not (trampoline ?from))
    )
    :effect (and
      (not (at ?a ?from))
      (at ?a ?to)
      (when (arrow ?to) (has-arrow ?a))
      (when (arrow ?to) (not (arrow ?to)))
      (when (arrow ?to) (empty ?to))
      (when (key ?to) (has-key ?a))
      (when (key ?to) (not (key ?to)))
      (when (key ?to) (empty ?to))
    )
  )

  (:action walk-off-map
    :parameters (?a - agent ?from - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (edge ?from ?dir)
      (not (trampoline ?from))
    )
    :effect (and
      (not (at ?a ?from))
      (free ?a)
    )
  )

  (:action push
    :parameters (?a - agent ?from - location ?middle - location ?to - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (adjacent ?from ?middle ?dir)
      (adjacent ?middle ?to ?dir)
      (or (crate ?middle) (trampoline ?middle))
      (or (empty ?to) (arrow ?to) (key ?to))
    )
    :effect (and
      (not (at ?a ?from))
      (at ?a ?middle)
      (when (crate ?middle) (not (crate ?middle)))
      (when (crate ?middle) (crate ?to))
      (when (trampoline ?middle) (not (trampoline ?middle)))
      (when (trampoline ?middle) (trampoline ?to))
      (when (empty ?to) (not (empty ?to)))
      (when (arrow ?to) (has-arrow ?a))
      (when (arrow ?to) (not (arrow ?to)))
      (when (key ?to) (has-key ?a))
      (when (key ?to) (not (key ?to)))
      (empty ?middle)
    )
  )

  (:action shoot
    :parameters (?a - agent ?from - location ?to - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (adjacent ?from ?to ?dir)
      (has-arrow ?a)
      (wumpus ?to)
    )
    :effect (and
      (not (has-arrow ?a))
      (not (wumpus ?to))
      (empty ?to)
    )
  )

  (:action unlock
    :parameters (?a - agent ?from - location ?to - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (adjacent ?from ?to ?dir)
      (has-key ?a)
      (door ?to)
    )
    :effect (and
      (not (has-key ?a))
      (not (door ?to))
      (empty ?to)
    )
  )

  (:action jump
    :parameters (?a - agent ?from - location ?over - location ?to - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (trampoline ?from)
      (adjacent ?from ?over ?dir)
      (adjacent ?over ?to ?dir)
      (or (empty ?to) (arrow ?to) (key ?to))
      (not (wall ?over))
    )
    :effect (and
      (not (at ?a ?from))
      (at ?a ?to)
      (when (arrow ?to) (has-arrow ?a))
      (when (arrow ?to) (not (arrow ?to)))
      (when (arrow ?to) (empty ?to))
      (when (key ?to) (has-key ?a))
      (when (key ?to) (not (key ?to)))
      (when (key ?to) (empty ?to))
    )
  )

  (:action jump-off-map
    :parameters (?a - agent ?from - location ?over - location ?dir - direction)
    :precondition (and 
      (at ?a ?from)
      (trampoline ?from)
      (adjacent ?from ?over ?dir)
      (edge ?over ?dir)
      (not (wall ?over))
    )
    :effect (and
      (not (at ?a ?from))
      (free ?a)
    )
  )
)