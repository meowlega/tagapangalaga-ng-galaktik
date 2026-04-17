Welcome, thanks for reading, this took time ..

# Introduction

If you want to understand why this project exist, what is the problem, and does it solves, you first need to understand the game itself.

<img width="1920" height="1080" alt="galaxy_life_main" src="https://github.com/user-attachments/assets/46af631b-866d-44ca-be85-72c68bab9357" />

Welcome to **Galaxy Life**. It's a massive multiplayer real-time strategy game. If you've ever played *Clash of Clans*, then you already got the basics. You progress by upgrading your *Base*, You build defenses to repel an attack, Train an army to attack other players, you get the idea. There's also *Alliances*, and *Wars*.

Even tho there is similarities, Galaxy Life and Clash of Clans greatly differs from each others. In Clash of Clans, you get 1 Main base, and maybe a different variants like *Builders base* and *Clan Capital*. But ultimately the Main base is the one who get all the attention for upgrades. And in Alliances and Wars, Main base is the one that gets hits.

Galaxy Life takes this approach differently. Instead of having 1 Main Base, your base becomes a **Planet**, a unique entitiy. By progressing in game, a Player could have up to *12 Planets*, where each Planets can fuction as a normal Main base. Meaning, you need to **manage 12 Clash of Clans Main Account** for this game to work.

As always, Galaxy life **Main Planet** is your very first planet to get in the game. For early game, you can just upgrade your *Storage* and upgrade your *Town Hall* up to level 3 without any problems. But as you get to Town Hall 4, things gets complex.

The maximum storage you can get by maxing every storage building in Town Hall level 3 is lets say **100,000 coins**, but in order to upgrade your Town Hall to level 4, we need **170,000** coins. Damn thats impossible. Solution? you colonize a new **Planet**, which is your **Planet #2**. You need to progress that new Planet of yours up to Town Hall 3 too so that you could get another max storage of 100,000 coins. Therefor, by game mechanic, combining both Planet resource, you could now upgrade to Town Hall level 4 by having 100,000 + 100,000 = 200,000 storage capacity. The mechanic continues to go like that.

By Town Hall level 6, you would reach the maximum storage allowed per Planet, which is 15,000,000 coins. But in order to upgrade to Town Hall 7, you need 40 Million, Town Hall 8, 80 Million, Town Hall 9, 120 Million. So in essence, you would need atleast *8 more Town Hall 6 Planets with Max Storage upgrade* just to reach the pinnacle of Town Hall 9, which is the max level of base allowed for Planets for now.

Not to mention that each Planet is an entity of their own. Each planets can **train its own troops**, can have resources buildings like gold mines and elixir, each unique upgrades for troops, meaning, if you unlocked a troop in Planet 1, and upgraded it to level 6 there, it won't get carried to Planet 2 and more. **All Planets are Independent to each other**, the only thing that gets merge is the resources.

# Colonization

Now that we know how a **Planet** functions, we can now go to the topic of **Colonization** and **Galaxy**.

Each Planet lies on an entity called **Galaxies**. each Galaxy can **contain up to maximum 12 Planets**. There are also different types of **Galaxies** but its not important right now. Theoretically, since you have up to max 12 Planets at disposal, you could *colonize an entire Galaxy of your own*, but thats for funsies.

Now because a single Galaxy cannot even hold all of your 12 Planets, what is the other mechanic? **Universe**. In the Universe, it acts like a 2D Cartesian plane grid, where each grid can contain a *unique galaxy*. Lets say in Universe(1,1), there lies a Galaxy named "Calisto". So the galaxy would be named **Calisto (1,1)**. Then in (3,1), there could be a **Andromeda (3,1)**. Not all coordinates in the Universe have a galaxy, but *only one galaxy can be at exact coordinate*. There is no Andromeda (3,1) and Calisto (3,1) .. It is not allowed.

As we say, we could have have max 9 Planets in one single Galaxy, or we could colonize different Galaxies nearby. We could have something like this:

Planet 1 Andromeda (3,1) *# Main Planet*

Planet 2 Andromeda (3,1) *# I want to put both of my Planets in Adromeda for fun*

Planet 3 Calisto (1,1)

Planet 4 Armik (100,23)

Planet 5 Nina (700,324)

Planet 6 Calisto (22,1001) *# Understand that Galaxy names can repeat, but their coordinates is what makes them unique!*

Planet 7 Melanthri (77,22)

...

Up to Planet 12

And so on .. You could literally put your planets at any point, anywhere in the Galaxy on the Universe. As long as there is a Galaxy at the edge of the Universe, you could put a Planet there. For the limits, as of now, the Universe at best is 1200 x 1200. That makes it 14,400,000 unique coordinates, but as I said, not all coordinates have a Galaxy. The estimated unique Galaxy count spread in the Universe is at most 1,000,000. But that is still goddamn many!

<img width="1920" height="1080" alt="sample_base" src="https://github.com/user-attachments/assets/fff3e70d-711f-40d0-b365-4ef717f57833" />

*Sample image of a Galaxy Life Base*

<img width="518" height="448" alt="planets_max" src="https://github.com/user-attachments/assets/8a5a453b-de82-4344-9a35-a38c7c2bd4db" />

*A player with 12 Planets*

<img width="667" height="554" alt="low_level_planets" src="https://github.com/user-attachments/assets/763a549b-0169-473f-a973-05b27e21de69" />

*A beginner player with few planets*

<img width="1920" height="1080" alt="galaxy_view" src="https://github.com/user-attachments/assets/6a7df818-e03b-47c1-a1d6-f21de6f2e867" />

*Galaxy View where the Planets exist*

<img width="1920" height="1080" alt="universe_view" src="https://github.com/user-attachments/assets/4843e160-1603-4bcf-b555-f371204d52f2" />

*Universe View, where the Galaxies exist*

<img width="1920" height="1080" alt="galaxy_view2" src="https://github.com/user-attachments/assets/12fdaeea-f417-4e80-8fed-af47ae0e4f1d" />

*UI when you click a Galaxy on the Universe*

Now lets go for the topic of attacking. We will compare Clash of Clans again to Galaxy Life, In Clash of Clans, when one Player attacked another, it is done into 1 attack only. Meaning if you didn't destroy the base in 1 attack, you are kinda cooked.

In Galaxy Life, things also get kinda complex. Here, **you can attack a Planet as many times as you want**. A Planet defense is really tough and overpowered. You are aware on how **different Planets can have independent trained troops**. Usually, to destroy a very good enemy base Planet, you need 4 consecutive attacks.

Lets say in Planet #1, you trained all units specifically just to destroy defenses, and you also queue units so that they are pre-trained already. There is a limit on pre-training but mind you that units on this damn game takes really long to train, maybe because you can split the training up to 12 Planets, but still.

Yeah in Planet #1, all of this can be units that destroy defenses, then on Planet #2, all of units are for *looting*. Suprisingly, resource buildings in this game is just damn tanky. And there's alot of factors to consider that you really need a *clean up crew*.

So yeah, the way it works usually is Enemy Planet 1 would be attacked by 2 Planets:

Attack #1: Enemy Planet gets attacked by Planet 1 anti defense troops. If successful, it should delete 50% of the defense or more.

Attack #2: Enemy Planet gets attacked once again by Planet 1 (now using the queued pre-trained units). If succesful, it should delete the rest of the defenses.

Attack #3: Assuming that there is now no defense, depending on amount of traps hidden, or the placements of the buildings and walls, you could *clean* the base with one go using Planet 2 cleaning troops.

Attack #4: Sometimes sht is really tough and you need a second cleaning attack, wiping the base 100% destroyed.

But yeah, this can vary, maybe you need to invest more in anti defense because enemy Planet base is too good, or you could do it in 1 go (rare) because the one who made the base makes it *free* or it was designed by a toddler.

There are planet rules tho, when a Planet is 100% destroyed, it will start a countdown, usually 3 hours. Then after that 3 hours, the Planet can be attacked once again! albeit maybe lower resource gain because you already looted it on first attack.

If you didn't 100% the base, it will foreverly not regenerate unless you destroy the remaining building, but the owner of the Planet can comes back (goes online) and regenerate their base manually.

Here's whats interesting, suppose you really hate that damn Player, you could use your Planet #1 and #2 to attack the hated Player Planet #1, but you want to destroy all that players base?. Now that is interesting. If it takes 2 Planets worth of units just to destroy 1 enemy Planet, then at most, if you are try hard, you could only destroy 6 enemy Planets, supposed that the enemy Planets are maxed out and have good defense, and your attacking Planet troops is upgraded and used with skill properly.

Also, because you attacked 6 Planets, you basically robbed that guy 6x of their resource. And there's even better rule! you know *Training Camps*, where the trained units stays? well .. **if training camp gets destroyed in attack, you lose all trained troops in that camp**, and when you come back, the ones will go out and fill the Training Camps are the ones you *queued*, and then you already have no *succeeding* troops to attack with.

This game can be grindy, cruel, competitive, but thats why I love it! I am a competitive person, same with my friends. I hope you understand the crazy mechanics of this game above, there's more but no need to deep dive really.

Alliances and Wars. In Clash of Clans, you can only attack 2x in Wars, but as I said in Galaxy Life, you could attack and destroy a Planet as many times as you can, the planet regeneration rules apply. In *Wars*, if you destroy a Planet, you get *Stars*, simple right? but what if that destroyed planet comes back again in 3 hours?, then you can destroy that Planet again and *earn even more Stars!*.

Lets get to the heart on **why this project is really important**. I have an Alliance inside this game named *Pinoy Warriors*. At the time I joined, I cursed you not we are **300 Wins & 2 Loss**. That is 99% winrate. We are legit all try hard, but as time goes on, it is really taxing on trying to keep tabs on the game. I want to make something that will help us gain an advantage while not being getting burnt out in game. This game, if played correctly, really tooks lots of free time of yours.

<img width="811" height="570" alt="highwinrate" src="https://github.com/user-attachments/assets/710ccdc8-98dc-4feb-8efc-7b4fb134e909" />

## Planet Placement Mechanics

In Wars, **The main Planet, or Planet #1 is always shown and available to attack**, Both enemy and us can attack the main Planet, as long as the Player is not online. Naturally, if the enemy is good, we both clears all main planet, and we get equal amount of *Stars*. But thats about it, because both us and enemy constantly and dilligently attacks main planet every 3 hours, the *Stars* are usually *tied*.

How to remove that *tie?*, **Attack the other Planets, or colonized Planets of enemy player**. Meaning, the wars are cat and mouse. If you are stupid enough to put your Planet #1 and Planet #2 in the same Galaxy (1,1), then the enemy could attack 2 Planets of yours every 3 hours, *leading to Star advantage!*, but what if they found even more Planets, as long as the Planets are found and enemy is dilligently doing their best to destroy it, then they will have a very big advantage.

War duration is always *3 days*, so the Alliance with the most Stars at the end of that duration, Wins. *There is no tie* in this game. There is some complex rules about it but at the end, its always Win or Loss.

One strategy to think and adapt is for us to put different Planets of ours far from each other in the Universe coordinate plane. One might do it like this:

Planet #1 Andromeda (1,1)
Planet #2 Elmer (200, 19)

As you can see, Planet #1 and #2 are so ridiculously far apart, even if the enemy scan to click every single galaxies from X: 1 to 200, it will take them *hours* just to do that. Not to mention you could also put other of your Planets anywhere.

Planet #3 Cocak (1000, 700)
Planet #4 Mintara (72, 890)
Planet #5 Jacakds (322, 256)
...
And so on ..

The more spaced your Planets are, and random your Planets, the **Harder it is to find in Wars**. If one Alliance really wanna win this war, they would spend a considerable amount of time to find the Planets of their enemy.

Now thats inefficient. Even me, I couldn't care less to click that damn Galaxies one by one and note all the Planets inside it for future reference. But we are competitive in War and would like not to lose if possible. Thats why I proposed a plan, **to somehow automate the collections of all planets in the universe**. This proves to be an endearing task for me.

Also, as you know, Alliance members can also help you attack a single Planet of enemy, well depending on your strategies. A member might have maxed our anti defense troops, so he/she might do well better at clearning defenses at planet, and your job is cleaning.

Now that the stage is setup, and you have a somewhat clear understanding on what it looks like to play the game, I can now safely tackle on the *steps* i did to make this thing a reality.

