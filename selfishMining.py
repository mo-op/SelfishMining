from forms import simulationForm
from flask import Flask, render_template, redirect, url_for, request
from math import ceil, floor
import random
import os
import sys
reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app._static_folder = "static"
app.config.update(dict(SECRET_KEY="powerful secretkey", WTF_CSRF_SECRET_KEY="a csrf secret key"))


####################################################################################################
# HELPER FUNCTIONS #
'''
 * Simulate awarding a Bitcoin block
 *  a => Percent of the total network owned by the selfish mining pool
 *  g => Gamma
'''
def awardBlock(a, g):
  #issue: random always returns honest
  #rnd = random.uniform(0, 1)
  #rnd = int(from_bytes(os.urandom(8), byteorder="big") / ((1 << 64) - 1))
  rnd = random.random()
  print rnd
  # Honest miners found a block on top of the selfish block
  if rnd > a and rnd <= (a + (1 - a) * g):
    return 'honest+'

  # Honest miners found a block
  elif rnd > (a + (1 - a) * g):
    return 'honest'

  #Selfish mining pool found a block
  else:
    return 'selfish'

def shiftList(a):
  temp = []
  for i in range(len(a)):
    if i > 0:
      temp.append(a[i])
  print temp
  if len(temp) == (len(a)-1):
    return temp
  else:
    return a

def float_round(num, direction = floor):
    places = 3
    return direction(num * (10**places)) / float(10**places)

####################################################################################################
@app.route('/',methods=['GET','POST'])
def index():
  '''
  Gets the input from the form values
  '''
  form = simulationForm()
  if request.method == 'POST':

    # values from form

    # Pool size of selfish miner
    alpha = float(request.form['alpha'])

    # Pool size of honest miner
    gamma = 0.4

    # Number of cycles to run the simulation
    iterations = int(request.form['iterations'])

    # Effective Network Hashpower (ENH) of each block held back by the selfish miner
    hiddenBlocks = []

    # Running tally of found blocks published by the honest miners while behind the selfish mining pool
    visibleBlocks = 0

    # Tally number of orphan blocks which get discarded
    orphanBlocks = 0

    # Total blocks found by the selfish mining pool
    selfishBlocks = 0

    # Num of block added to the valid blockchain
    publicChain = 0
    # Assume that the public chain has blocks as selfish mining comes into play after a certain number of blocks have been mined
    # publicChain.append(1)
    # publicChain.append(1)
    # publicChain.append(1)
    # publicChain.append(1)
    # publicChain.append(1)

    x = 1

    curState = 0

    results = True

    error_val = False

    while True:
      '''
      The next step depends on the state of the system
      '''
      if curState == 0:
        '''
        This is the initial state
        '''
        awardedTo = awardBlock(alpha,gamma)
        print awardedTo

        if awardedTo == 'selfish':
          hiddenBlocks.append(1)
          selfishBlocks += 1
          curState = 1
          results = True

        elif awardedTo == 'honest':
          publicChain += 1
          results = True
          curState = 0

        else:
          curState = 0

      elif curState == 1:
        '''
        The selfish mining pool is finding itself ahead by at least one block.
        '''
        awardedTo = awardBlock(alpha,gamma)
        print awardedTo 

        if awardedTo == 'selfish':
          hiddenBlocks.append(alpha)
          #selfishBlocks += 1
          results = True

        elif awardedTo == 'honest':
          publicChain += 1
          # If the selfish mining pool was more than two blocks ahead, it publishes one 
          # The oldest block in the competing honest miner chain is invalidated & the state remains the same
          if len(hiddenBlocks) - publicChain == 1:
            publicChain += len(hiddenBlocks)
            hiddenBlocks.pop()

          elif len(hiddenBlocks) - publicChain > 1:
            curState = 0
            
          #   selfishBlocks+= 1
          #   orphanBlocks+= 1

          #   publicChain += len(hiddenBlocks)
          #   publicChain-= 1
          #   results = True

          # # If the selfish mining pool was just two blocks ahead, it publishes its entire chain
          # # All honest miner blocks in the branch are invalidated & State returns to the initial state
          # elif (len(hiddenBlocks) - publicChain > 2): 
            
          #   if (len(hiddenBlocks) > 2):
          #     print("Unusual condition, hidden block length: "+str(len(hiddenBlocks)))
          #     error_val = "Unusual condition, hidden block length: "+str(len(hiddenBlocks))
          #     results = False
              
          #   while (len(hiddenBlocks)):
          #       selfishBlocks+= 1
          #       publicChain += len(hiddenBlocks)
            
          #   orphanBlocks += visibleBlocks
          #   visibleBlocks = 0
          #   curState = 0

          # If the selfish mining pool was only one block ahead, it publishes its block and hopes (f)
          # Two blocks will be awarded in systemState -1
          elif (len(hiddenBlocks) == publicChain):
            if (len(hiddenBlocks) != 1):

              print("Unusual condition, hidden block length: "+str(len(hiddenBlocks))) # Should never see this
              error_val = "Unusual condition, hidden block length: "+str(len(hiddenBlocks))
              results = False
              publicChain = 0
              curState = -1

            else:
              print("Unusual condition, hidden block length: "+str(len(hiddenBlocks))+" visible block length: "+str(visibleBlocks)) # Should never see this
              error_val = "Unusual condition, hidden block length: "+str(len(hiddenBlocks))+" visible block length: "+str(visibleBlocks)
              results = False
          #break

        else:
          pass 

      elif curState == -1:
        '''
        Block race i.e. both pools competing to become the longest chain
        '''
        awardedTo = awardBlock(alpha,gamma)
        print awardedTo

        if awardedTo == 'honest+':
          '''
          Honest miners find the block which extends the selfish chain, each group wins one block and state is back to the initial one 
          '''
          selfishBlocks += 1
          publicChain += 2
          # publicChain.append(shiftList(hiddenBlocks))
          # publicChain.append(alpha + (1 - alpha) * gamma)
          curState = 0
          results = True

        elif awardedTo == 'honest':
          '''
          Honest miners find the block which extends their chain and win two blocks
          '''
          hiddenBlocks = []
          publicChain += 2
          # publicChain.append(1 - alpha)
          # publicChain.append((1 - alpha) - (1 - alpha) * gamma)
          curState = 0
          results = True

        elif awardedTo == 'selfish':
          '''
          Selfish mining pool finds the block and wins two blocks
          '''
          selfishBlocks += 2
          
          #publicChain.append(shiftList(hiddenBlocks))
          # publicChain.append(alpha + (1 - alpha) * gamma)
          curState = 0
          results = True

        else:
          pass 

        orphanBlocks += 1
      
      else:
        '''
        continue
        '''
        continue

      # # NOT SURE considering difficulty: allocate blocks until iterations are complete
      if publicChain >= iterations:
        #If prev state was -1, two blocks were added. Remove the last one
        if publicChain > iterations:
          publicChain -= 1
        
      x += 1
      if x > int(iterations):
        break

    ## breakpoint

    # formatting the results
    print selfishBlocks, publicChain
    #print float(selfishBlocks)/float(publicChain)

    num_selfish = selfishBlocks
    new_difficulty = float_round((publicChain / int(iterations)))
    theoretical = float((alpha*(1-alpha)**2*(4*alpha+gamma*(1-2*alpha))-alpha**3)/(1-alpha*(1+(2-alpha)*alpha)))
    simulated = float(selfishBlocks)/float(publicChain)
    return render_template('index.html',form=form,results=results,num_selfish=num_selfish,new_difficulty=new_difficulty,num_orphaned=orphanBlocks,theoretical=theoretical,simulated=simulated)
  return render_template('index.html',form=form)

if __name__ == '__main__':
   app.run(debug = True)
