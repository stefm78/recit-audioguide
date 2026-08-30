# Palette sonore sémantique — L’Odyssée

## Principe

Ce document décrit les besoins artistiques. Il ne prétend pas que chaque asset existe déjà.

Audio Engine sait déjà exécuter les rôles nécessaires :

- texture ;
- punctuation ;
- scene ;
- bridge ;
- carry mesuré v6 ;
- ducking ;
- fades ;
- espaces acoustiques bornés.

Aucun nouveau rôle moteur n’est demandé.

## Familles de matière

### Mer / navigation

Besoins sémantiques :

- ressac proche ;
- eau contre coque ;
- rame ;
- bois de coque ;
- cordage ;
- voile / gréement ;
- vent faible ;
- vent fort ;
- vague ponctuelle ;
- tempête ;
- calme marin presque sans texture.

Règle : ne jamais utiliser une unique mer générique pour tous les états.

### Ithaque / maison

- feu discret ;
- bois intérieur ;
- textile / métier ;
- repas ;
- vaisselle ;
- pas ;
- animaux domestiques ponctuels ;
- arc / corde tendue.

### Grotte du Cyclope

- moutons ;
- pierre / déplacement de masse ;
- feu ;
- respiration proche ;
- bruit de pas lourd ou impact, si crédible.

Aucune grotte ambiante continue n’est nécessaire si l’espace acoustique et quelques événements suffisent.

### Circé

- foyer ;
- animaux ponctuels ;
- repas ;
- extérieur calme.

Le son doit rendre le confort dangereux, pas l’exotisme.

### Enfers

Besoin volontairement minimal :

- très peu de texture ;
- éventuellement vent ou espace sourd extrêmement discret ;
- voix ;
- silence.

### Sirènes

Le besoin principal est vocal, pas un asset de bruitage.

Éventuellement :

- mer très retirée ;
- cordage ;
- coque.

### Scylla / Charybde

- eau violente ponctuelle ;
- bois sous contrainte ;
- voix de l’équipage ;
- pas de rugissement de monstre générique si aucune source convaincante.

### Retour / porcherie

- feu ;
- animaux ;
- extérieur terrestre ;
- pas ;
- porte / bois.

### Argos

Le chien ne doit pas devenir un effet de bibliothèque émotionnel.

Un son animal peut être absent. La scène peut fonctionner par narration, respiration et environnement.

### Lit

- bois ;
- textile ;
- respiration ;
- silence.

Pas de musique de résolution obligatoire.

## Espaces acoustiques disponibles

Utilisables sans évolution moteur :

- dry ;
- outdoor-open ;
- small-stone-room ;
- large-stone-interior ;
- confined-stone.

Correspondances possibles :

- grotte : confined-stone, avec prudence ;
- palais : large-stone-interior ponctuel, pas sur toutes les voix ;
- maison / chambre : dry ou small-stone-room très léger ;
- extérieur / mer : outdoor-open.

## Stratégies de transition

### Narratrice → Ulysse conteur

Aucun effet obligatoire.

Le transfert d’attention peut venir d’un court silence, d’une phrase de demande, puis du changement de voix.

### Cyclope → mer

Une scene ou un bridge peut laisser la matière de la grotte céder au large sans musique.

### Cloison monde vivant → Enfers

Réduction de couches, pas montée d’effets.

### Phéaciens → Ithaque

Le trajet peut être très court ; Ulysse dort. Ne pas fabriquer un montage de voyage.

### Combat → Pénélope

Après la violence, réduire fortement la densité avant la scène de reconnaissance.

## Assets existants utiles

La bibliothèque consumer possède déjà un asset rivière, mais il ne faut pas le réutiliser pour simuler automatiquement la mer.

Les assets historiques médiévaux actuels ne sont pas considérés comme palette grecque par défaut.

## Gaps attendus

Avant le premier probe, il faudra qualifier seulement les assets réellement utilisés par les scènes probe.

Probables besoins nouveaux :

- sea-surf ;
- wooden-boat ;
- rope-rigging ;
- strong-wind ;
- sheep ;
- fire-hearth ;
- bow-string ;
- restrained-dog-presence si la scène l’exige.

La recherche exhaustive de tous les sons de 85 minutes est interdite avant le Production Plan.

## Règle de coût

Un asset n’entre dans le catalogue de production que si :

1. une intention narrative le demande ;
2. une source libre/compatible est qualifiée ;
3. sa provenance est durable ;
4. sa durée et sa qualité conviennent au rôle ;
5. son absence ne serait pas meilleure.
