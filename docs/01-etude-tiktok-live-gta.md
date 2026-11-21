# Étude : business TikTok LIVE GTA automatisé

*Phase 1 : recherche, concepts, classement, recommandation. Aucun code n'a été écrit, en attente de validation.*
*Recherche effectuée le 21/11/2026.*

---

## 0. Conclusion en premier (à lire avant tout le reste)

> **Un LIVE GTA 100 % automatisé, 24 h/24 et sans présence humaine, est contraire aux règles de monétisation de TikTok LIVE.**
> Les *LIVE Monetization Guidelines* (extraits cités par la recherche, voir §2) rendent inéligibles aux cadeaux :
> - « content generated or operated primarily through automated systems, such as AI or other third-party tools, **without meaningful creator presence, interaction, or facilitation** of the LIVE experience » ;
> - « content that is largely **passive or unattended** » ;
> - les vidéos préenregistrées, montées ou en boucle présentées comme du direct.

**Conséquence :** le modèle économiquement viable, et celui que je recommande, est un **jeu automatisé avec un animateur présent**.
- Le gameplay GTA tourne seul : personne ne conduit et personne ne contrôle de personnage.
- Le système gère aussi les manches, les événements et les cadeaux.
- **Vous** (ou un co-animateur) êtes présent, au micro et idéalement à la caméra, pour commenter, réagir et modérer, pendant des sessions de durée humaine (par exemple 2 à 4 h). Vous ne faites aucun « gameplay ».

Le système vous libère du jeu. Il ne vous libère pas de la présence. C'est l'automatisation qui est vendable et conforme, pas l'absence.

Autres constats bloquants ou structurants :

| Sujet | Constat | Statut |
|---|---|---|
| GTA 6 | Sorti le 19/11/2026 sur **PS5 et Xbox Series uniquement**. Aucune version PC annoncée, donc **aucun modding possible**. | Fait vérifié (Take-Two, 09/11/2026), voir sources |
| GTA V PC | Moddable en **mode Histoire** via Script Hook V + ScriptHookVDotNet (Legacy) ou SHVDN Enhanced, avec BattlEye désactivé. | Fait vérifié (sources concordantes), **non testé par moi** |
| Pont TikTok vers GTA V | Il existe des outils : Crowd Control (GTA V supporté), un plugin GTA 5 dans TikFinity, et un plugin open source en C# (smeysu). | Fait vérifié (existence). Fonctionnement **non testé** |
| Droits Rockstar | La politique vidéo Rockstar autorise l'usage **non commercial**. Un LIVE monétisé sort de ce cadre ; une licence est possible (copyright@take2games.com). | Fait vérifié (texte de la politique). Niveau de risque réel : **hypothèse** |
| Cadeaux déclenchant des effets en jeu | C'est un format reconnu (« Interactive Games » de LIVE Studio, selon des guides). Interdits : jeux de hasard, tombolas, promesses trompeuses, échange cadeau contre engagement. | Partiellement vérifié (sources secondaires) |

---

## 1. Méthode et limites de la recherche

- **Outils utilisés** : moteur de recherche web (résumés de résultats), puis tentative de lecture directe des pages officielles TikTok.
- **Pages officielles TikTok** (`tiktok.com/live/creators/...` et `tiktok.com/legal/...`) : **non lisibles depuis mon environnement**. Elles s'affichent en JavaScript et ont renvoyé un contenu vide, même dans un navigateur sans interface. Les citations ci-dessous proviennent des extraits indexés par la recherche. **Vérifiez-les dans l'application ou sur le site.**
- **TikTok, YouTube et Reddit (vidéos et LIVE)** : je n'ai pu ni regarder de LIVE ni lire de commentaires. Les « exemples observés » proviennent donc de **descriptions écrites** (articles, pages produits, dépôts), pas d'une observation directe.
- **GitHub** : je n'ai pas lu directement le code des dépôts cités, seulement leurs descriptions.
- Je n'ai trouvé **aucune statistique fiable** d'audience ou de revenus pour des LIVE GTA interactifs. **Je n'en donne donc aucune.**

Légende utilisée : **[FAIT]** vérifié par une source citée · **[OBS]** exemple décrit par une source · **[HYP]** hypothèse de ma part · **[EST]** estimation chiffrée avec hypothèses explicites.

---

## 2. Recherche

### 2.1 LIVE GTA interactifs et outils existants

| Solution | Ce qui est établi | Statut |
|---|---|---|
| **Crowd Control** | Intégration TikTok LIVE lancée en **mai 2025** après plus d'un an de bêta fermée. Les follows, likes, partages et cadeaux déclenchent des effets dans plus de 150 jeux, dont **GTA V**. Une offre gratuite existe avec un nombre limité d'effets liés à des cadeaux par jeu ; les chiffres diffèrent selon les pages (3 ou 5). | [FAIT] existence ; [OBS] limites |
| Crowd Control, guide GTA V | Supporte **uniquement GTA V Legacy, version Steam ou Epic**. Nécessite Script Hook V et la désactivation des mises à jour automatiques de Steam. Le retour à une version antérieure du jeu n'est pas supporté officiellement. | [FAIT] (page guide) |
| **TikFinity** (zerody) | Outil tiers populaire. Propose un « GTA 5 TikFinity Plugin » : les spectateurs déclenchent des actions en jeu via des cadeaux. Fournit aussi des webhooks. | [FAIT] existence ; fonctionnement [OBS] |
| **smeysu/GTA5-TikTok-Integration** | Plugin GTA 5 en C#, licence MIT, piloté par webhooks (TikFinity recommandé). Version v1.1.1 selon un agrégateur. | [OBS] (agrégateur, dépôt non lu) |
| TikOps, Shulex | Annoncent des « GTA gift challenges ». Ce sont des pages marketing. | [OBS], faible fiabilité |
| **Chaos Mod V** (gta-chaos-mod) | Environ 350 effets aléatoires, vote du chat **Twitch**, mode overlay OBS. La fourche WebChaosModV (vote web) est archivée depuis le 02/11/2024. | [FAIT] |
| Trollstorm Control, Bits for Tricks | Mods GTA V d'interaction Twitch, cités sur gta5-mods. | [OBS] |

**Ce que cela signifie [HYP] :** le créneau « les cadeaux déclenchent du chaos dans GTA » **existe déjà et s'outille en quelques heures** avec Crowd Control ou TikFinity. Un LIVE « chaos aléatoire » de plus aura du mal à se distinguer. **La différenciation doit venir du format** (structure de jeu, identité des spectateurs, enjeux, récurrence), pas de la simple connexion entre cadeau et effet.

### 2.2 LIVE où les cadeaux déclenchent des événements (hors GTA)

- **Minecraft** : mod « TikTok Live Connector » sur CurseForge (likes, commentaires et cadeaux déclenchent des événements). Format « TNT Challenge » mentionné par la presse française (LADN), sans détail sur le mécanisme. [OBS]
- **Jeux conçus pour TikTok LIVE** : itch.io regorge de jeux (« Crowns & Carnage », jeux « tiktok-interactive-games », EarnOnLIVE, BeetGames, ScrollPlay) où les cadeaux font apparaître des unités, des obstacles ou des bonus. [OBS]
- **Roblox, Unity** : des créateurs construisent leurs propres jeux à cadeaux (LADN, Canberra Times). [OBS]
- **Format natif TikTok « LIVE Match / battles »** : les cadeaux et les likes valent des points, l'équipe ou le créateur qui en a le plus gagne. Des matchs « cadeau spécifique » sont possibles. [FAIT] (centre d'aide TikTok via extraits)

### 2.3 LIVE automatisés avec des personnages contrôlés par ordinateur

- **Neuro-sama** (Twitch) : streameuse IA, présentée par Tubefilter comme la plus abonnée de Twitch à un moment donné. [OBS]
- **Claude Plays Pokémon** (Twitch) : une IA joue en direct et son raisonnement est affiché à l'écran. Projet expérimental mené par des membres d'Anthropic. [OBS]
- Chaînes IA « 24/7 » sur Twitch et YouTube (AI Jesus, VTuber pachislot, orchestrateurs de hackathon). [OBS]
- **Limite clé :** ces exemples sont sur **Twitch ou YouTube**, qui ont des règles différentes. Sur TikTok, l'automatisation sans présence significative du créateur est **explicitement inéligible à la monétisation** (§2.6). [FAIT]
- Je n'ai trouvé **aucun exemple documenté** de LIVE GTA TikTok où un personnage IA joue seul en continu. [FAIT : absence de résultat, pas preuve d'absence]

### 2.4 Mécaniques qui génèrent des commentaires et retiennent dans la durée

Synthèse de game design tirée des exemples ci-dessus. Les mécaniques sont observées ; leur efficacité est **[HYP]**.

1. **Identité** : le spectateur *existe* dans le jeu (son pseudo sur un personnage, une voiture, un classement). C'est le levier le plus fort pour la participation gratuite (`!join`).
2. **Manches courtes avec une fin nette** (3 à 5 min) : un suspense et un climax réguliers, et une raison de rester « pour la prochaine ».
3. **Camps opposés** (aide contre chaos, rouge contre bleu) : ils génèrent naturellement des commentaires. Le format « battle » natif de TikTok montre que la mécanique est familière.
4. **Records et classements persistants** (jour, semaine, saison) : ils donnent une raison de **revenir**.
5. **Imprévisibilité bornée** : du chaos, mais dans une structure lisible en 2 secondes (un nouveau spectateur doit comprendre immédiatement).
6. **Rendez-vous fixes** (même heure, finale hebdomadaire) : c'est la fidélisation classique des LIVE.
7. **Le gratuit a un vrai pouvoir** : like, commentaire et vote changent quelque chose. Les cadeaux ajoutent du spectacle, pas l'unique moyen d'influer. C'est aussi ce qui évite la pression à la dépense.

### 2.5 Solutions techniques TikTok vers jeu

| Brique | Option | Notes |
|---|---|---|
| Lire les événements LIVE (commentaires, likes, cadeaux, follows) | **TikTok-Live-Connector** (Node.js, MIT) ou **TikTokLive** (Python, isaackogan) | **Non officiels** (rétro-ingénierie du service WebCast). Ils peuvent casser lors d'une mise à jour TikTok, ce qui s'est déjà produit (versions < 1.1.7 hors service). [FAIT] |
| | **TikFinity** (webhooks) | Tiers, utilisé par de nombreux créateurs. Une offre gratuite limitée existe ; tarifs à vérifier. [OBS] |
| | **Crowd Control** | Solution clé en main. Moins de liberté de game design. [FAIT] |
| | API officielle TikTok | Les webhooks officiels (developers.tiktok.com) concernent d'autres usages. **Je n'ai trouvé aucune API officielle publique d'événements LIVE pour les cadeaux.** [FAIT : absence de résultat] |
| Diffusion | **TikTok LIVE Studio** (Windows, officiel) ou **OBS** avec clé de stream RTMP | La clé de stream n'est pas disponible pour tous les comptes ni toutes les régions. Le seuil d'abonnés n'est pas publié de façon fiable. [OBS] |
| Overlay | Page web locale en « source navigateur » (LIVE Studio et OBS) | Méthode standard. [OBS] |

### 2.6 Règles TikTok (France)

Les sources principales sont les *LIVE Monetization Guidelines*, les *Community Guidelines* (mise à jour 2025 H2) et la *LIVE Gift Policy*. Elles ont été lues via des extraits, car les pages ne s'affichent pas depuis mon environnement.

| Question | Réponse | Statut |
|---|---|---|
| Un compte exclu de Creator Rewards peut-il recevoir des cadeaux LIVE ? | Ce sont **deux programmes distincts**. L'inéligibilité au CRP n'exclut pas automatiquement les cadeaux LIVE. **Mais** si l'exclusion vient d'infractions (statut du compte dégradé), la *LIVE Gift Policy* exige un compte « in good standing ». | [FAIT] programmes distincts (sources secondaires) ; impact sur votre compte : **inconnu** |
| Conditions pour les cadeaux | 18 ans minimum pour envoyer ou recevoir, compte en règle, pays éligible. Seuil d'abonnés incertain : la plupart des sources disent environ 1 000, certaines divergent. | [FAIT] âge ; [OBS] seuils |
| Comment vérifier ? | (1) Paramètres → Compte → **Statut du compte** : avertissements et restrictions. (2) Outils pour créateurs / **LIVE Center** : présence et activation des cadeaux LIVE. (3) Lancer un LIVE test et vérifier que l'**icône Cadeaux** est disponible pour les spectateurs. Libellés exacts **à confirmer dans l'app**. | [OBS] |
| LIVE entièrement automatisé autorisé ? | Diffuser n'est pas interdit en soi, mais c'est **inéligible à la monétisation** sans présence, interaction ou facilitation significative du créateur. Le passif ou non surveillé est aussi inéligible. | [FAIT] |
| Contenu répétitif | Les créateurs qui diffusent de façon répétée un contenu sous les standards de qualité peuvent voir leur **visibilité ou leurs fonctionnalités LIVE limitées**. Boucles et préenregistré présentés comme du direct : inéligibles. | [FAIT] |
| Présence humaine nécessaire ? | Pour la monétisation : **oui, en pratique** (« meaningful creator presence »). TikTok ne publie pas de durée minimale ; la ligne exacte reste **floue**. | [FAIT] principe ; seuil : inconnu |
| Incitations interdites | Promesses trompeuses ; échanges artificiels (« follow-for-follow », « cadeau contre like ou follow ») ; sollicitation **mécanique et répétitive** de cadeaux ; **jeux de hasard, tombolas ou tirages liés aux cadeaux** ; présenter les cadeaux comme des dons ; renvoyer vers l'extérieur de la plateforme. | [FAIT] (lignes directrices) et [OBS] (guides) |
| Événements déclenchés par des cadeaux | Format reconnu : LIVE Studio propose des « Interactive Games » où les cadeaux déclenchent des effets en jeu. Le LIVE reste soumis à toutes les règles. | [OBS] (guides citant l'aide LIVE Studio) |
| Sanctions | Arrêt du LIVE, interdiction temporaire de LIVE, perte temporaire des cadeaux, restrictions de visibilité. Bannissement en cas de récidive ou de tentative de contournement. | [FAIT] |

**Conséquences de design (non négociables) :**
- aucun tirage au sort ni aucune « chance de gagner » quelque chose de valeur via un cadeau ;
- aucun lot réel ni récompense hors plateforme ;
- jamais « envoie X pour que je... » répété en boucle par un bot ;
- le gratuit doit pouvoir gagner ;
- un humain est présent et interagit.

### 2.7 Analyse technique GTA

| Point | Constat | Statut |
|---|---|---|
| GTA 6 plateformes | PS5 et Xbox Series X/S. Sorti le 19/11/2026. **Pas de PC annoncé** ; une rumeur (GamesBeat) parle de début 2027, non confirmée. | [FAIT] / rumeur [OBS] |
| GTA 6 modding | Impossible sur console : pas de scripts ni d'automatisation sans contourner les protections, **exclu**. | [FAIT] |
| GTA V PC | Deux éditions : **Legacy** et **Enhanced**. Mode Histoire moddable. | [FAIT] |
| Script Hook V | Bibliothèque de scripts natifs. Doit correspondre exactement à la version du jeu : chaque patch Rockstar la casse jusqu'à sa mise à jour. | [FAIT] |
| ScriptHookVDotNet / **SHVDN Enhanced** | Permet d'écrire des scripts en **C#**. La fourche Enhanced (Chiheb-Bacha) supporte Legacy et Enhanced ; elle date de septembre 2025, avec des mises à jour au moins jusqu'en juillet 2026. | [FAIT] |
| BattlEye | Depuis septembre 2024 (mise à jour 1.69). Désactivable pour le mode Histoire (option du Launcher ou `-nobattleye`). Sans BattlEye, **pas d'accès à GTA Online**, ce qui est voulu. | [FAIT] |
| Mods et GTA Online | **Interdit** : risque de bannissement. Le projet reste **100 % mode Histoire, hors ligne**. | [FAIT] |
| Conduite autonome | Tâches natives de l'IA du jeu (`TASK_VEHICLE_DRIVE_WANDER`, conduite vers un point). Des mods existants (Seamless Autonomous Driving, AutoDriver, Tesla Autopilot) le prouvent. Certains rapports font état de crashs sur Enhanced avec certains mods. | [FAIT] existence ; fiabilité longue durée **non testée** |
| PNJ combattants, poursuites | Natifs connus (apparition de peds, armes, tâches de combat ou de fuite, niveau de recherche). Chaos Mod V en utilise des centaines. | [FAIT] (général) ; **non testé** par moi |
| Communication jeu vers application externe | Un script C# peut ouvrir un serveur local (HTTP, WebSocket ou named pipe sur 127.0.0.1). Le plugin smeysu le fait via webhooks. | [OBS] ; standard en .NET |
| Politique Rockstar sur les mods | Take-Two « generally will not take legal action » contre les projets **solo, non commerciaux**, respectant la PI de tiers (page mise à jour le 06/01/2025). Cette politique est révocable. | [FAIT] |
| Politique vidéo Rockstar | Usage autorisé si **non commercial**. Monétiser des images de jeu sort de cette autorisation ; une licence au cas par cas est possible via copyright@take2games.com. | [FAIT] |

**Faisabilité de l'automatisation complète [HYP, à tester] :**
- **Réaliste** : un script qui fait tourner des manches seul, sans intervention ; des personnages IA qui combattent, courent ou fuient ; des effets déclenchés par des événements externes.
- **Risques réels** :
  - PNJ ou véhicules bloqués : il faut un « chien de garde » qui détecte et téléporte ;
  - fuites mémoire ou crash après plusieurs heures : il faut un redémarrage automatique ;
  - mise à jour du jeu qui casse Script Hook : il faut bloquer les mises à jour ;
  - déconnexion de la librairie TikTok non officielle : il faut une reconnexion et un mode dégradé.
- **Une arène fermée est bien plus fiable que le monde ouvert** : moins de PNJ coincés, une caméra maîtrisée, des performances prévisibles. C'est un critère majeur du classement.
- **Je ne peux promettre aucune stabilité de plusieurs heures avant des tests d'endurance réels sur votre PC.**

---

## 3. Dix concepts originaux (+1)

Pour tous les concepts :
- **Technique commune** : GTA V PC en mode Histoire, un mod C# (SHVDN), un orchestrateur local qui reçoit les événements TikTok, un overlay web, et un animateur humain présent.
- **Coût** : voir §6 (quasi identique d'un concept à l'autre, hors temps de développement).
- **Risque TikTok commun** : monétisation refusée sans présence humaine ; tout tirage ou lot interdit.

### C1. « LOS SANTOS ROYALE » : l'arène des spectateurs
- **Principe** : une zone fermée de la carte. Chaque manche de 3 à 4 min oppose jusqu'à environ 20 combattants IA, **chacun portant le pseudo d'un spectateur** qui a tapé `!join`. Le dernier debout gagne.
- **Ce que voit le spectateur** : une caméra aérienne dynamique, les pseudos au-dessus des têtes, la liste des survivants, un chrono et un « kill feed ».
- **Ce que fait le jeu automatiquement** : apparition des combattants, combat via les tâches IA, rétrécissement de la zone, caméra qui suit l'action, annonce du vainqueur, nouvelle manche.
- **Participation gratuite** :
  - `!join` pour entrer ;
  - commentaire `!soutien <pseudo>` (pas d'effet de jeu, juste un compteur de « public ») ;
  - les likes collectifs remplissent une jauge qui déclenche un événement d'arène (largage d'armes, brouillard).
- **Cadeaux (si éligible)** :
  - petits cadeaux : effets cosmétiques et légers (gilet, son, ralenti) ;
  - moyens : événements d'arène (chien d'attaque, voiture folle, ragdoll) ;
  - rares : « Frappe aérienne », « Tank », « Mode lune » (gravité).
  - **Plafonds** : un même effet a un temps de recharge, et aucun effet ne garantit une victoire.
- **Pourquoi c'est divertissant** : on voit **son nom** se battre, les retournements sont fréquents, une fin nette arrive toutes les 3 min.
- **Pourquoi rester** : « je suis inscrit pour la manche suivante », classement du jour.
- **Renouvellement** : modificateurs de manche tirés au sort par le jeu (armes, météo, heure, gravité). Rotation de 5 à 10 arènes. Modes spéciaux (duel, équipes).
- **Anti-répétition** : table de modificateurs avec historique (pas deux fois le même d'affilée) ; « manche spéciale » toutes les 30 min.
- **Longues sessions** : l'état est réinitialisé à chaque manche, ce qui limite l'accumulation d'erreurs. Le chien de garde est simple dans un espace fermé.
- **Difficultés** : affichage des pseudos (texte 3D), équilibrage de l'IA, limite de PNJ et performances, caméra automatique lisible en vertical 9:16.
- **Risques TikTok** : si les cadeaux « boostent son combattant », il y a une pression « payer pour gagner ». Il faut donc des effets bornés et une majorité de vainqueurs gratuits. Aucun lot réel.

### C2. « GRAND PRIX DE LOS SANTOS » : courses de voitures des spectateurs
- **Principe** : 8 à 16 voitures IA portant les pseudos (`!join`) courent sur des circuits balisés de la carte. Manches de 2 à 3 min.
- **Ce que voit le spectateur** : caméra de course (hélico ou poursuite), classement en direct, nom du leader.
- **Ce que fait le jeu automatiquement** : apparition des voitures, conduite IA par checkpoints, détection des voitures bloquées (replacement), podium.
- **Gratuit** : `!join`, vote du circuit suivant (commentaire), jauge de likes qui déclenche « pluie » ou « nuit ».
- **Cadeaux** : turbo, flaque d'huile, police à la poursuite du leader, « tous changent de véhicule », pluie de rochers.
- **Divertissement** : c'est l'esprit « course de billes » appliqué à GTA ; dépassements et crashs spectaculaires.
- **Fidélisation** : championnat hebdomadaire par points, pilotes « vétérans ».
- **Renouvellement** : circuits multiples, classes de véhicules, météo.
- **Difficultés** : l'IA de conduite de GTA est **peu fiable sur circuit** (trajectoires, blocages) ; il faut des circuits testés un par un. Le circulation PNJ doit être gérée. **Faisabilité moyenne.**
- **Risques TikTok** : les mêmes que C1. Pas de paris.

### C3. « LE CONVOI » : défense de fourgon blindé
- **Principe** : un fourgon conduit par l'IA traverse la ville de A à B. Des gardes du corps PNJ (pseudos des spectateurs, `!join`) l'escortent. Des vagues d'assaillants arrivent.
- **Gratuit** : `!join` pour devenir garde ; likes qui réparent le fourgon.
- **Cadeaux** : *camp Défense* (blindage, hélico allié) contre *camp Attaque* (barrage, gang, hélico ennemi). Deux camps donc, comme une battle.
- **Divertissement** : « tower defense » mobile ; le suspense « arrivera ou pas ».
- **Renouvellement** : itinéraires multiples, types de cargaison, boss.
- **Difficultés** : un convoi en monde ouvert subit les aléas de l'IA de conduite (bouchons, accidents) et beaucoup d'entités en mouvement. **Faisabilité moyenne-faible.**
- **Risques** : équilibre entre les camps. Pas de pari sur l'issue.

### C4. « WANTED : SURVIVRE » : la cavale aide contre chaos
- **Principe** : un fugitif IA démarre une cavale avec un niveau de recherche. Le chat se divise en **Aide** (bleu) et **Chaos** (rouge). Objectif : battre le record de survie.
- **Ce que voit le spectateur** : la poursuite, les étoiles de recherche, un chrono contre le record, une jauge Aide/Chaos.
- **Ce que fait le jeu automatiquement** : fuite IA (véhicule, puis à pied), changement de véhicule, gestion de la mort, puis nouvelle cavale.
- **Gratuit** : commentaire `bleu` ou `rouge` (vote toutes les 30 s pour le prochain événement), likes vers la jauge.
- **Cadeaux** : Aide (soin, véhicule blindé, perte d'une étoile) contre Chaos (+1 étoile, barrage, hélico, tank).
- **Divertissement** : poursuites de GTA (le cœur du jeu), affrontement entre équipes.
- **Fidélisation** : record du jour et de la semaine, « fugitifs » nommés d'après les meilleurs soutiens.
- **Difficultés** : une IA de fuite crédible en monde ouvert (blocages, mort trop rapide) ; une caméra de poursuite. **Faisabilité moyenne.**
- **Risques** : même vigilance sur les deux camps.

### C5. « TAXI INFERNAL »
- **Principe** : un taxi IA doit livrer des clients ; le chat choisit la destination ; les cadeaux sèment des embûches. Compteur de « courses réussies ».
- **Points faibles** : rythme plus lent, moins d'identité des spectateurs. Monde ouvert (blocages).

### C6. « LE MAIRE DE LOS SANTOS »
- **Principe** : toutes les 2 min, le chat vote une « loi » parmi 3 (gravité lunaire, voitures roses, émeute, piétons agressifs, tsunami de voitures). La caméra se promène dans la ville pour montrer les effets.
- **Points forts** : technique simple (proche de Chaos Mod), très bon levier de commentaires.
- **Points faibles** : peu d'enjeu et peu de fin nette ; **risque de « contenu passif »** et ressemblance forte avec Chaos Mod existant.

### C7. « CRASH LAB » : records de physique
- **Principe** : un mannequin ou un véhicule est catapulté (rampe, avion, canon). Le score est la distance ou les « dégâts ». Records du jour.
- **Gratuit** : vote du lanceur ou de la rampe ; likes qui ajoutent de la vitesse.
- **Cadeaux** : lanceurs spéciaux (fusée, jet, explosion).
- **Points forts** : très fiable techniquement (séquences courtes et déterministes), très « clipable ».
- **Points faibles** : répétitif à long terme, peu d'identité des spectateurs.

### C8. « GUERRE DES QUARTIERS » : carte persistante
- **Principe** : les spectateurs rejoignent l'un des 4 gangs (couleurs). Chaque manche est un affrontement pour un quartier ; une **carte de territoire persistante** évolue sur des jours ou des semaines (saisons).
- **Points forts** : fidélisation maximale (on revient défendre son gang), originalité.
- **Points faibles** : complexité (persistance, équilibrage, plusieurs zones). **C'est une évolution naturelle de C1**, pas un point de départ.

### C9. « LE PERSONNAGE QUI OBÉIT AU CHAT » (via un modèle de langage)
- **Principe** : un modèle de langage traduit les commentaires en actions autorisées pour un personnage.
- **Points faibles** :
  - risque de modération (contenu des commentaires lus ou affichés) ;
  - coût d'API ;
  - latence ;
  - **risque accru vis-à-vis de la règle « contenu opéré par IA sans présence du créateur »**.
- À éviter au lancement.

### C10. « CATASTROPHE CITY »
- **Principe** : un quartier subit des catastrophes croissantes (incendies, crashs aériens, inondation simulée, météo extrême). Les spectateurs votent ce qui arrive ensuite et une jauge de « survie de la ville » évolue.
- **Points faibles** : beaucoup d'effets sont limités sans mods lourds (pas de vraie inondation dynamique), et le format manque de héros identifiables.

### C11 (bonus). « L'ÉVASION DE BOLINGBROKE »
- **Principe** : des détenus IA (pseudos) tentent de s'évader de la prison ; les cadeaux aident ou font échouer.
- C'est une variante thématique de C1 réutilisable comme « arène » spéciale.

---

## 4. Classement objectif

Grille : Engagement /25 · Cadeaux /20 · Faisabilité /20 · Fidélisation /15 · Originalité /10 · Coût-maintenance /10.
*Notes = jugement d'analyste argumenté [HYP], pas mesure. Un score d'engagement élevé ≠ revenus garantis.*

| # | Concept | Eng. | Cad. | Faisa. | Fidél. | Orig. | Coût | **Total** |
|---|---|---|---|---|---|---|---|---|
| C1 | Los Santos Royale (arène) | 23 | 18 | 16 | 14 | 7 | 8 | **86** |
| C4 | Wanted : Survivre | 21 | 17 | 15 | 11 | 6 | 8 | **78** |
| C2 | Grand Prix de Los Santos | 21 | 16 | 13 | 13 | 7 | 7 | **77** |
| C8 | Guerre des quartiers | 20 | 17 | 11 | 14 | 9 | 6 | **77** |
| C3 | Le Convoi | 20 | 17 | 12 | 11 | 8 | 7 | **75** |
| C7 | Crash Lab | 18 | 15 | 17 | 10 | 6 | 9 | **75** |
| C6 | Le Maire de Los Santos | 16 | 13 | 17 | 10 | 5 | 8 | **69** |
| C10 | Catastrophe City | 17 | 15 | 13 | 9 | 6 | 8 | **68** |
| C5 | Taxi infernal | 15 | 13 | 12 | 9 | 7 | 7 | **63** |
| C9 | Personnage piloté par LLM | 18 | 12 | 8 | 10 | 9 | 4 | **61** |
| C11 | Évasion de Bolingbroke | (variante de C1, non classée séparément) | | | | | | |

Justification des critères décisifs :
- **Faisabilité** : arène fermée (C1, C7) > monde ouvert avec IA de conduite (C2, C3, C4).
- **Engagement et fidélisation** : formats où le spectateur a une **identité** (C1, C2, C8) > formats où il ne fait que voter (C6, C10).
- **Originalité** : C6 et C10 ressemblent à ce que font déjà Chaos Mod et Crowd Control.

---

## 5. Les trois meilleurs : comparaison et simulation de 5 minutes

### Comparaison

| | C1 Los Santos Royale | C4 Wanted : Survivre | C2 Grand Prix |
|---|---|---|---|
| Lisibilité en 2 s | Très bonne (« dernier debout ») | Bonne (« survivre ») | Très bonne (« course ») |
| Identité du spectateur | Son pseudo combat | Son camp (bleu/rouge) | Son pseudo pilote |
| Gratuit vraiment influent | Oui (`!join`, jauge de likes) | Oui (votes de camp) | Oui (`!join`, vote circuit) |
| Fin nette et fréquente | Toutes les 3 à 4 min | Variable (1 à 10 min) | Toutes les 2 à 3 min |
| Fiabilité IA | **Élevée** (zone fermée) | Moyenne (monde ouvert) | Moyenne-faible (IA sur circuit) |
| Rendu vertical 9:16 | Bon (caméra aérienne) | Bon (poursuite) | Moyen (circuits larges) |
| Risque « pay-to-win » | Moyen, à borner | Faible (effets sur un tiers) | Moyen, à borner |
| Réutilisation du moteur | Base pour C8, C11 et C2 | Partielle | Partage le système de pseudos de C1 |

### Simulation C1 : « Los Santos Royale » (5 min)
*Exemple fictif : les pseudos, cadeaux et réactions sont imaginés pour illustrer.*

- **00:00** Écran « MANCHE 47 : Arène du Port. Modificateur : BROUILLARD ». En haut, « 18/20 inscrits ». L'animateur : « Encore deux places, tapez `!join` ! » Les commentaires défilent : `!join`, `!join`.
- **00:15** 20 combattants apparaissent en cercle, le pseudo au-dessus de la tête (« @lea_92 », « @kevgta »...). Compte à rebours 3-2-1, tous ont un pistolet.
- **00:30** Premiers tirs. Le kill feed affiche « @kevgta a éliminé @mathis.fr ». En haut à droite, « 19 survivants ». La caméra aérienne zoome sur un duel.
- **00:50** La jauge de likes du public atteint 100 % : « LARGAGE ! » Une caisse tombe au centre, trois combattants courent dessus et l'un récupère un fusil à pompe.
- **01:20** Un spectateur envoie un petit cadeau. Bandeau « @nina_s offre un GILET à @lea_92 » ; effet sonore, contour bleu sur le personnage. L'animateur remercie brièvement et commente l'action, sans relance.
- **01:45** La zone rétrécit (cercle rouge au sol). « 11 survivants ». Les combattants hors zone perdent de la vie.
- **02:10** Un cadeau moyen : « VOITURE FOLLE ! » Une voiture sans conducteur fonce dans la mêlée et trois PNJ partent en ragdoll. Les commentaires réagissent fortement.
- **02:40** Vote gratuit affiché : « Dernière minute : GRAVITÉ LUNAIRE ou PLUIE DE BALLES ? Tapez 1 ou 2 ». Le 1 l'emporte et les survivants rebondissent au ralenti.
- **03:20** Duel final : « @lea_92 contre @tom.zz ». Ralenti automatique au dernier tir.
- **03:30** « VICTOIRE : @lea_92 (gratuit, 3e victoire du jour) ». Classement du jour affiché 10 s. L'animateur félicite.
- **03:45 à 05:00** Écran d'inscription de la manche 48 : « Arène : Chantier. Modificateur : NUIT + COUTEAUX ». L'animateur discute avec le chat, présente les records et accueille les nouveaux. Les inscriptions se remplissent.

### Simulation C4 : « Wanted : Survivre » (5 min)
*Exemple fictif.*

- **00:00** « CAVALE #12. Record du jour : 6:42 ». Le fugitif IA vole une voiture devant le commissariat ; 2 étoiles. Jauge « AIDE ■■■□□ CHAOS ».
- **00:20** Poursuite en ville ; les commentaires « bleu » et « rouge » s'affrontent. Au bout de 30 s, le vote donne Chaos 60 % : « +1 ÉTOILE ! » Un hélicoptère arrive.
- **01:10** Cadeau Aide : « VÉHICULE BLINDÉ ». La voiture du fugitif est remplacée en pleine course.
- **01:50** Cadeau Chaos : « BARRAGE ». Des voitures de police bloquent le pont ; le fugitif fait demi-tour par le canal.
- **02:30** La jauge de likes est pleine : « NUIT TOMBE ». La visibilité baisse.
- **03:10** Crash ; le fugitif finit à pied, 4 étoiles. L'animateur commente, et les commentaires « bleu » se multiplient.
- **03:40** Vote : Aide l'emporte, « PERTE D'UNE ÉTOILE ».
- **04:30** Tank (cadeau rare Chaos). Le fugitif est éliminé à 4:28. Écran « 4:28, record non battu (6:42). Équipe gagnante : CHAOS ».
- **04:45** Nouvelle cavale qui démarre.

### Simulation C2 : « Grand Prix de Los Santos » (5 min)
*Exemple fictif.*

- **00:00** « GP #31 : Circuit Vinewood Hills, 3 tours. 12/12 pilotes inscrits ». Grille de départ avec pseudos.
- **00:20** Départ, la caméra hélico suit la course ; classement en direct à gauche.
- **00:50** Cadeau : « HUILE devant le leader ». Le leader part en tête-à-queue et le 3e prend la tête.
- **01:30** Jauge de likes : « PLUIE ». Adhérence réduite, deux sorties de route.
- **02:00** Une voiture bloquée est replacée automatiquement : « ⚠ RÉINITIALISATION @xx ».
- **02:40** Dernier tour au ralenti à la ligne : « @sam.r gagne ! +10 pts championnat ».
- **03:00 à 05:00** Podium, vote du circuit suivant (`1`, `2`, `3`), nouvelles inscriptions.

---

## 6. Business

### 6.1 Coûts de fonctionnement [EST]

| Poste | Hypothèse | Coût |
|---|---|---|
| GTA V PC | Vous le possédez déjà ? Sinon, prix Steam ou Epic du moment (non vérifié ici) | 0 € ou prix d'achat |
| Script Hook V, SHVDN(E), OBS, Node.js ou Python | Gratuits | 0 € |
| TikTok LIVE Studio | Gratuit | 0 € |
| TikFinity ou Crowd Control (optionnel) | Offres gratuites limitées ; offres payantes non vérifiées | 0 € au départ |
| **Électricité** | PC de jeu : environ 200 à 300 W à la prise en jeu (mesures autour de 206 à 320 W pour une config RTX 4060, selon le processeur). Prix 0,2001 €/kWh (tarif Bleu, option Base, 3 à 6 kVA, novembre 2026). | Voir ci-dessous |
| Matériel | Micro (vous en avez probablement un), webcam facultative | 0 à 60 € |

Électricité, à 250 W en moyenne :
- **3 h/jour** (format recommandé) : 0,25 × 3 × 30 = 22,5 kWh/mois, soit **environ 4,5 €/mois** ;
- **24 h/24** (déconseillé) : 0,25 × 24 × 30 = 180 kWh/mois, soit **environ 36 €/mois**, plus l'usure matérielle.

**Le vrai coût est votre temps** : développement (estimation au §7), présence en LIVE, maintenance après les patchs du jeu.

### 6.2 Monétisation : ce qu'on peut affirmer

- Revenus TikTok : cadeaux (pièces converties en diamants), sous réserve d'éligibilité. Le taux de conversion et la part de TikTok ne sont **pas confirmés par une source officielle que j'ai pu lire** ; le chiffre d'environ 50 % souvent cité est non vérifié. Les montants doivent se lire dans votre app.
- **Aucune projection de revenus n'est fournie** : sans données réelles de vos LIVE, toute projection serait inventée.
- **Seuil de rentabilité monétaire** : les coûts directs sont d'environ 5 à 40 €/mois, donc ils sont couverts très tôt *si* les cadeaux sont actifs. La vraie question est la **rentabilité de votre temps**, à mesurer après 4 semaines de tests.
- **Scénario prudent à construire avec vos données**, après environ 10 LIVE :
  `revenu mensuel ≈ (diamants moyens par heure de LIVE) × (heures de LIVE par mois) × (valeur d'un diamant lue dans l'app)`.
  On décidera de continuer ou d'arrêter sur cette base mesurée.
- **Risque juridique Rockstar** : un LIVE monétisé sort de l'autorisation « non commerciale ». Énormément de streamers monétisent du GTA ; je n'ai **pas** trouvé de cas d'action contre eux, mais c'est une absence de preuve, pas une garantie. Option prudente : écrire à copyright@take2games.com.

### 6.3 Indicateurs à suivre

- **Audience** : spectateurs simultanés moyens et pic, durée moyenne de visionnage, nouveaux abonnés par LIVE, taux de retour (pseudos déjà vus).
- **Interaction** : commentaires par minute, % de spectateurs faisant `!join`, likes par minute.
- **Monétisation** (si éligible) : diamants par heure, nombre de donateurs distincts. Surveiller la **concentration** : beaucoup de revenus venant d'une seule personne est un signal de risque, pas de succès.
- **Technique** : crashs par heure, durée moyenne entre deux incidents, reconnexions TikTok, latence entre cadeau et effet.
- **Conformité** : avertissements ou restrictions reçus (zéro toléré).

### 6.4 Stratégie de lancement

1. **Vérifier l'éligibilité** (statut du compte, cadeaux LIVE, accès LIVE Studio ou clé de stream) **avant tout développement lourd**.
2. Prototype hors ligne (mode test sans TikTok), puis tests d'endurance.
3. 3 à 5 LIVE « bêta » courts (1 h) annoncés à vos 15 k abonnés.
4. **Créneau fixe** quotidien ou 5 soirs par semaine, plus une « finale du dimanche ».
5. Vidéos courtes tirées des meilleurs moments : même sans Creator Rewards, elles font découvrir le LIVE.
6. Profiter de l'actualité GTA 6 en marketing seulement (titres, hashtags), **sans spoilers** (Rockstar fait retirer les spoilers et cinématiques isolées), sans logo officiel et sans se faire passer pour Rockstar.

### 6.5 Fidélisation et évolution

- Statistiques persistantes par pseudo (victoires, éliminations), titres (« Vétéran », « Légende du Port »), saisons mensuelles.
- Évolution prévue : C1 (arène), puis C11 (prison) en événement spécial, puis C2 (Grand Prix) partageant le même système de pseudos, puis C8 (guerre des quartiers persistante).
- Plusieurs formats en rotation dans la semaine, ce qui répond aussi au risque de « contenu répétitif ».

---

## 7. Recommandation

### ✅ Je recommande **C1 « Los Santos Royale »**, en format animé (jeu automatique et animateur présent).

**Pourquoi celui-ci, et pas le plus spectaculaire :**
1. **Faisabilité** : une zone fermée et des manches réinitialisées limitent les deux grands risques d'un LIVE long (IA bloquée, erreurs qui s'accumulent).
2. **Divertissement** : voir **son pseudo** se battre crée une identité et des réactions ; une fin nette toutes les 3 à 4 min ; lisible en 2 secondes.
3. **Gratuit réellement influent** (`!join`, jauge de likes, votes), ce qui est sain et conforme. Les cadeaux restent du spectacle, avec des plafonds.
4. **Différenciation** face à Crowd Control, TikFinity et Chaos Mod : ce n'est pas du chaos aléatoire, c'est un **jeu structuré dont les spectateurs sont les acteurs**.
5. **Socle réutilisable** : C2, C8 et C11 se construisent sur le même moteur.

**Ce que ce projet n'est pas :** une machine à revenus passive 24 h/24. Ce modèle est explicitement inéligible à la monétisation TikTok.

### Estimation de développement [EST, à affiner après validation]

| Étape | Contenu | Ordre de grandeur |
|---|---|---|
| 0. Vérifications | Éligibilité TikTok, édition de GTA V, specs du PC, Script Hook fonctionnel | 1 à 2 h (vous et moi) |
| 1. Prototype du mod | Arène, apparitions, combat IA, pseudos, fin de manche ; mode test avec faux événements | 1 à 2 semaines de soirées |
| 2. Orchestrateur | Connexion aux événements TikTok, règles (temps de recharge, plafonds, file d'attente), arrêt d'urgence | ~1 semaine |
| 3. Overlay et tableau de bord | Classement, inscrits, effets, supervision, journaux | ~1 semaine |
| 4. Endurance | Sessions de 3 à 6 h hors ligne, corrections, chien de garde, redémarrage | 1 à 2 semaines |

Ces durées supposent que vous testez sur votre PC Windows : je ne peux pas exécuter GTA V depuis mon environnement. **Aucune fonctionnalité ne sera déclarée « fonctionnelle » sans test réel de votre côté.**

---

## 8. Questions avant de lancer le développement

1. **Validez-vous C1 « Los Santos Royale »** (ou préférez-vous C4 ou C2) ?
2. **Acceptez-vous le format « animateur présent »** ? Combien d'heures par jour ou par semaine êtes-vous prêt à être en LIVE (même sans jouer) ?
3. Quelle **édition de GTA V** possédez-vous (Legacy ou Enhanced ; Steam, Epic ou Rockstar) ?
4. **Specs du PC** : processeur, carte graphique, mémoire vive. Le même PC fera tourner GTA V et l'encodage du LIVE.
5. Résultats des vérifications TikTok : **statut du compte**, **cadeaux LIVE disponibles ?**, accès à **LIVE Studio** ou à une **clé de stream** ?
6. Préférence de langage : C# pour le mod (imposé par SHVDN), avec **Python** ou **Node.js** pour l'orchestrateur ?

---

## 9. Sources

*Dates : date de publication ou de mise à jour quand elle est connue ; sinon « n. d. ». Toutes consultées le 21/11/2026 via recherche web. Les pages officielles TikTok n'ont pas pu être affichées directement.*

**TikTok (règles)**
- LIVE Monetization Guidelines (n. d.) : https://www.tiktok.com/live/creators/en-US/rules_and_guidance/live_monetization_guidelines
- Community Guidelines, Accounts & Features (2025 H2) : https://tiktok.com/community-guidelines/en/accounts-features?cgversion=2025H2update
- LIVE Gift Policy (n. d.) : https://www.tiktok.com/legal/page/global/live-gift-policy/en
- LIVE Match, aide TikTok (n. d.) : https://support.tiktok.com/nl/live-gifts-wallet/tiktok-live/live-match
- Creator Rewards, éligibilité (n. d.) : https://support.tiktok.com/en/business-and-creator/creator-rewards-program/creator-rewards-program-eligibility
- Guides secondaires (fiabilité moyenne) : https://blog.tikfinity.com/tiktok-live-rules/ · https://livecade.io/docs/fix-live-restrictions/ · https://tiklivegames.io/articles/tiktok-live-gift-game-rules · https://streamlineagency.eu/guides/live-gaming-interactif-tiktok?lang=en · https://www.sirency.com/blog/how-to-make-money-on-tiktok-live · https://ttcalculator.net/learn/how-to-qualify-for-tiktok-live/ · https://manychat.com/blog/tiktok-live-monetization/

**Outils et LIVE interactifs**
- Crowd Control sur TikTok LIVE (annonce, mai 2025) : https://crowdcontrol.live/crowd-control-is-now-on-tiktok-live-let-the-chaos-begin/ · https://www.gamedeveloper.com/press-release/crowd-control-launches-tiktok-support-with-exclusive-interactive-features · https://crowdcontrol.live/tiktok
- Crowd Control, guide GTA V (n. d.) : https://crowdcontrol.live/guides/gtav · offres : https://crowdcontrol.live/Pro
- TikFinity (n. d.) : https://tikfinity.zerody.one
- smeysu/GTA5-TikTok-Integration : https://github.com/smeysu/GTA5-TikTok-Integration · https://kandi.openweaver.com/csharp/smeysu/GTA5-TikTok-Integration
- TikTok-Live-Connector : https://github.com/zerodytrash/TikTok-Live-Connector/releases · TikTokLive (Python) : https://github.com/isaackogan/TikTokLive/wiki/
- Chaos Mod V : https://www.gta5-mods.com/scripts/chaos-mod-v-beta · WebChaosModV (archivé le 02/11/2024) : https://github.com/CaveFire/WebChaosModV
- Minecraft TikTok Live Connector : https://www.curseforge.com/minecraft/mc-mods/tiktok-live-connector
- Canberra Times, TikFinity et le format interactif (n. d.) : https://www.canberratimes.com.au/story/9389858/the-audience-is-the-controller-tikfinity-and-the-new-live-format/
- LADN (TNT Challenge) : https://www.ladn.eu/?p=688947
- Jeux TikTok sur itch.io : https://tiktok-interactive-games.itch.io · https://earnonlive.itch.io
- Neuro-sama, Tubefilter : https://www.tubefilter.com/?p=190133 · Bloomberg (16/06/2023) : https://www.bloomberg.com/news/newsletters/2023-06-16/neuro-sama-an-ai-twitch-influencer-plays-minecraft-sings-karaoke-loves-art

**GTA V et GTA 6 (technique et légal)**
- Plateformes GTA 6 : https://www.gtalab.gg/en/news/gta-6-platforms-list-2026 · https://tech-insider.org/gta-6-pc-release-date-steam-epic-2026/ · https://dotesports.com/gta/news/gta-6
- Rockstar, PC Single-Player Mods (mise à jour 06/01/2025) : https://support.rockstargames.com/articles/5NVOAYjcTomO8v6SX2k76k/pc-single-player-mods
- Rockstar, politique vidéo et matériel protégé (n. d.) : https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz
- BattlEye et GTA V (support Rockstar) : https://support.rockstargames.com/en-US/articles/ocorZr1KpQE8WvoHE3gBG/battleye-troubleshooting-for-grand-theft-auto-v · GamingOnLinux (09/2024) : https://www.gamingonlinux.com/2024/09/grand-theft-auto-v-gets-battleye-anti-cheat-breaks-online-play-on-steam-deck-linux/page=2
- SHVDN Enhanced (première publication 18/09/2025) : https://github.com/Chiheb-Bacha/scripthookvdotnetenhanced · https://www.gta5-mods.com/tools/script-hook-v-net-enhanced
- Mods de conduite autonome : https://www.gta5-mods.com/scripts/tesla-autopilot-full-self-driving · https://www.gta5-mods.com/id/scripts/autodriver-mod · https://www.gta5-mods.com/ro/scripts/seamless-autonomous-driving-mod-no-keys-menus-or-buttons

**Coûts**
- Consommation d'un PC avec RTX 4060 : https://www.kitguru.net/components/graphic-cards/dominic-moass/nvidia-rtx-4060-review-ft-msi/39/ · https://en.overclocking.com/test-gigabyte-rtx-4060-windforce-oc-8g/9/
- Prix du kWh, tarif Bleu (novembre 2026) : https://www.hellowatt.fr/electricite-et-gaz/tarif-reglemente-energie · https://www.laprimeenergie.fr/energie/comparateur-fournisseur-electricite/tarif/prix-kwh
