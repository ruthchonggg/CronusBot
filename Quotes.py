from random import randrange

#--
quote_bank = ["_\"Today is your opportunity to build the tomorrow you want.\” \n- Ken Poirot_ \n",
              "_\"Believe you can and you’re halfway there.\"_\n",
              "_\"You have to expect things of yourself before you can do them.\" _ \n",
              "_\"Successful and unsuccessful people do not vary greatly in their abilities. They vary in their desires to reach their potential.\" \n – John Maxwell_\n",
              "_\"The secret of success is to do the common things uncommonly well.\" \n– John D. Rockefeller_\n",
              "_\"Good things come to people who wait, but better things come to those who go out and get them.\"_\n",
              "_\"Success is the sum of small efforts, repeated day in and day out.\"\n- Robert Collier_ \n",
              "_\"The secret to getting ahead is getting started.\"_\n",
              "_\"You don’t have to be great to start, but you have to start to be great.\"_\n",
              "_\"There are no shortcuts to any place worth going.\" \n- Beverly Sills_ \n",
              "_\"Push yourself, because no one else is going to do it for you.\"_\n",
              "_\"Some people dream of accomplishing great things. Others stay awake and make it happen.\"_\n",
              "_\"There is no substitute for hard work.\" \n– Thomas Edison_ \n",
              "_\"The difference between ordinary and extraordinary is that little “extra.\"_\n",
              "_\"You don’t always get what you wish for; you get what you work for.\"_\n",
              "_\"It’s not about how bad you want it. It’s about how hard you’re willing to work for it.\"_\n",
              "_\"The only place where success comes before work is in the dictionary.\" \n- Vidal Sassoon_ \n",
              "_\"Challenges are what make life interesting. Overcoming them is what makes life meaningful.\" \n- Joshua J. Marine_ \n",
              "_\"Don’t let what you cannot do interfere with what you can do.\" \n- John Wooden_ \n",
              "_\"You’ve got to get up every morning with determination if you’re going to go to bed with satisfaction.\" \n- George Lorimer_ \n",
              "_\"Procrastination makes easy things hard and hard things harder.\" \n- Mason Cooley_ \n",
              "_\"You don’t have to be great to start, but you have to start to be great.\" \n- Zig Ziglar_ \n",
              "_\"The way to get started is to quit talking and begin doing.\" \n- Walt Disney_ \n",
              "_\"I think it’s possible to ordinary people to choose to be extraordinary.\" \n- Elon Musk_ \n",
              "_\"The best way to predict your future is to create it.\" \n- Abraham Lincoln_ \n",
              "_\"Success doesn’t come to you, you’ve got to go to it.\" \n- Marva Collins_ \n",
              "_\"The secret of your success is determined by your daily agenda.\" \n- John C. Maxwell_ \n",
              "_\"Action is the foundational key to all success.\" \n- Pablo Picasso_ \n",
              "_\"Though no one can go back and make a brand-new start, anyone can start from now and make a brand-new ending.\" \n- Carl Bard_ \n",
              "_\"Procrastination is the art of keeping up with yesterday.\" \n- Don Marquis_ \n",
              "_\"I find that the harder I work, the more luck I seem to have.\" \n- Thomas Jefferson_ \n",
              "_\"Nobody can go back and start a new beginning, but anyone can start today and make a new ending.\" \n-  Maria Robinson_ \n",
              "_\"Whoso neglects learning in his youth, loses the past and is dead for the future..\" \n-  Euripides_ \n"]

def getQuote():
    limit = len(quote_bank) - 1
    num = randrange(limit)
    return (quote_bank[num])



