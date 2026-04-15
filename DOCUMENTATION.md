Welcome, thanks for reading, this took time ..

# Introduction

If you want to understand why this project exist, what is the problem, and does it solves, you first need to understand the game itself.

Welcome to **Galaxy Life**. It's a massive multiplayer real-time strategy game. If you've ever played *Clash of Clans*, then you already got the basics. You progress by upgrading your *Base*, You build defenses to repel an attack, Train an army to attack other players, you get the idea. There's also *Alliances*, and *Wars*.

Even tho there is similarities, Galaxy Life and Clash of Clans greatly differs from each others. In Clash of Clans, you get 1 Main base, and maybe a different variants like *Builders base* and *Clan Capital*. But ultimately the Main base is the one who get all the attention for upgrades. And in Alliances and Wars, Main base is the one that gets hits.

Galaxy Life takes this approach differently. Instead of having 1 Main Base, your base becomes a **Planet**, a unique entitiy. By progressing in game, a Player could have up to *12 Planets*, where each Planets can fuction as a normal Main base. Meaning, you need to **manage 12 Clash of Clans Main Account** for this game to work.

As always, Galaxy life **Main Planet** is your very first planet to get in the game. For early game, you can just upgrade your *Storage* and upgrade your *Town Hall* up to level 3 without any problems. But as you get to Town Hall 4, things gets complex.

The maximum storage you can get by maxing every storage building in Town Hall level 3 is lets say **100,000 coins**, but in order to upgrade your Town Hall to level 4, we need **170,000** coins. Damn thats impossible. Solution? you colonize a new **Planet**, which is your **Planet #2**. You need to progress that new Planet of yours up to Town Hall 3 too so that you could get another max storage of 100,000 coins. Therefor, by game mechanic, combining both Planet resource, you could now upgrade to Town Hall level 4 by having 100,000 + 100,000 = 200,000 storage capacity. The mechanic continues to go like that.

By Town Hall level 6, you would reach the maximum storage allowed per Planet, which is 15,000,000 coins. But in order to upgrade to Town Hall 7, you need 40 Million, Town Hall 8, 80 Million, Town Hall 9, 120 Million. So in essence, you would need atleast *8 more Town Hall 6 Planets with Max Storage upgrade* just to reach the pinnacle of Town Hall 9, which is the max level of base allowed for Planets for now.

Not to mention that each Planet is an entity of their own. Each planets can **train its own troops**, can have resources buildings like gold mines and elixir, each unique upgrades for troops, meaning, if you unlocked a troop in Planet 1, and upgraded it to level 6 there, it won't get carried to Planet 2 and more. **All Planets are Independent to each other**, the only thing that gets merge is the resources.

# Colonization

Now that we know how a **Planet** functions, we can now go to the topic of **Colonization** and **Galaxy**.

Each Planet lies on an entity called **Galaxies**. each Galaxy can **contain up to maximum 9 Planets**. There are also different types of **Galaxies** but its not important right now. Theoretically, since you have up to max 12 Planets at disposal, you could *colonize an entire Galaxy of your own*, but thats for funsies.

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
