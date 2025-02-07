import submitjobs
import os
import terminate as term
import time
import keyfilemodifications as keymods
import restraints as res
import sys
import mdtraj as md
import itertools
import numpy as np


def ExecuteLooseMinimization(poltype,boxfilename,keyfilename,outputname,jobtolog,jobtojobpath,jobtoinputfilepaths,jobtooutputfiles,jobtoabsolutebinpath):
    """
    Intent:
    Input:
    Output:
    Referenced By: 
    Description: 
    """
    cmd=MinimizeCommand(poltype,boxfilename,keyfilename,poltype.loosemincriteria,outputname)
    jobtolog[cmd]=poltype.outputpath+poltype.looseminjobsfilename
    jobtojobpath[cmd]=poltype.outputpath
    jobtoinputfilepaths[cmd]=[poltype.outputpath+boxfilename,poltype.outputpath+keyfilename,poltype.outputpath+poltype.prmfilepath]
    jobtooutputfiles[cmd]=[outputname,boxfilename+'_2']
    absbinpath=poltype.which(poltype.trueminimizepath)
    jobtoabsolutebinpath[cmd]=absbinpath
    return jobtolog,jobtojobpath,jobtoinputfilepaths,jobtooutputfiles,jobtoabsolutebinpath


def MinimizeCommand(poltype,xyzfilename,keyfilename,gradrms,outputfilename):
    """
    Intent:
    Input:
    Output:
    Referenced By: 
    Description: 
    """
    if poltype.externalapi!=None:
        minimizepath=poltype.minimizeommpath
    else:
        minimizepath=poltype.trueminimizepath
    cmd=minimizepath+' '+xyzfilename+' -k '+keyfilename+' '+str(gradrms)+' '+'> '+outputfilename
    return cmd



def RestrainWatersIonsInPocket(poltype,key):
    """
    Intent:
    Input:
    Output:
    Referenced By: 
    Description: 
    """
    for index in poltype.indicestorestrain:
        resposstring='restrain-position -'+str(index)+' '+str(index)+' '+str(poltype.restrainpositionconstant)+' '+'0'+'\n'
        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
        resposstring='# restrain-position for water or ions in pocket\n'
        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)


def CheapMinimizationProtocol(poltype):
    """
    Intent:
    Input:
    Output:
    Referenced By: 
    Description: 
    """
    if poltype.minfinished==False:
        
        if poltype.complexation==True:
            aaxis=poltype.aaxislist[0]
            baxis=poltype.baxislist[0]
            caxis=poltype.caxislist[0]
            ls=[aaxis,baxis,caxis]
            combs=itertools.combinations(ls, 2)
            poltype.needrot=False
            for comb in combs:
                diff=np.abs(comb[0]-comb[1])
                if diff>10:
                    poltype.needrot=True

            if poltype.needrot==True:        
                poltype.norotpair=FindTwoAtomsForRestrainingRotation(poltype) 
                for keyidx in range(len(poltype.configkeyfilename)):
                    if keyidx==0:
                        key=poltype.configkeyfilename[keyidx][0]
                        resposstring='restrain-position -'+str(poltype.norotpair[0])+' '+str(poltype.norotpair[0])+' '+str(poltype.restrainpositionconstant)+' '+str(poltype.norotrestrainsphereradius)+'\n'
                        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
                        resposstring='# restrain-position for preventing protein from rotating\n'
                        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
                        resposstring='restrain-position -'+str(poltype.norotpair[1])+' '+str(poltype.norotpair[1])+' '+str(poltype.restrainpositionconstant)+' '+str(poltype.norotrestrainsphereradius)+'\n'
                        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
                        resposstring='# restrain-position for preventing protein from rotating\n'
                        keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
            
    
    
        if poltype.restrainatomsduringminimization:
            for keyidx in range(len(poltype.configkeyfilename)):
                key=poltype.configkeyfilename[keyidx][0]
                
                ligandindices=poltype.ligandindices[keyidx]

                if keyidx==0 and poltype.binding==True:
                    resposstring='restrain-position -'+str(ligandindices[0])+' '+str(ligandindices[-1])+' '+str(poltype.restrainpositionconstant)+' '+'0'+'\n'
                    keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)

                    resposstring='restrain-position -'+str(1)+' '+str(poltype.totalreceptornumber)+' '+str(poltype.restrainpositionconstant)+' '+'0'+'\n'
                    keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)
                    key=poltype.configkeyfilename[keyidx][0]
                    RestrainWatersIonsInPocket(poltype,key)
                else:
                    resposstring='restrain-position -'+str(ligandindices[0])+' '+str(ligandindices[-1])+' '+str(poltype.restrainpositionconstant)+' '+'0'+'\n'
                    keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)

                resposstring='# restrain-position for protein and ligand atoms\n'
                keymods.AddKeyWord(poltype,poltype.outputpath+key,resposstring)

        willsubmit=False
        jobtolog={}
        jobtojobpath={}
        jobtoinputfilepaths={}
        jobtooutputfiles={}
        jobtoabsolutebinpath={}

        for i in range(len(poltype.minboxfilename)):
            minboxfilename=poltype.minboxfilename[i]
            key=poltype.configkeyfilename[i][0]
            boxfilename=poltype.boxfilename[i]
            output=poltype.looseminoutput[i]
            finished=term.CheckFileTermination(poltype,poltype.outputpath+output)[0]
            if not finished: # currently, only minimize and equilibraite default prm set
                poltype.WriteToLog('Minimizing system ',prin=True)
                willsubmit=True
                jobtolog,jobtojobpath,jobtoinputfilepaths,jobtooutputfiles,jobtoabsolutebinpath=ExecuteLooseMinimization(poltype,boxfilename,key,output,jobtolog,jobtojobpath,jobtoinputfilepaths,jobtooutputfiles,jobtoabsolutebinpath)
    
        if willsubmit==True:
            submitjobs.SubmitJobs(poltype,jobtolog,jobtojobpath,jobtoinputfilepaths,jobtooutputfiles,jobtoabsolutebinpath,poltype.outputpath+poltype.looseminjobsfilename)
    
        messages=[]
        for i in range(len(poltype.looseminoutput)):
            output=poltype.looseminoutput[i]
            minboxfilename=poltype.minboxfilename[i]
            boxfilename=poltype.boxfilename[i]
            minpymolboxfilename=poltype.minboxfilenamepymol[i]
            key=poltype.configkeyfilename[i][0]
            while term.CheckFileTermination(poltype,poltype.outputpath+output)[0]==False:
                msg='Loose minimization is not complete '
                if msg not in messages:
                    poltype.WriteToLog(msg,prin=True)
                    messages.append(msg)
                time.sleep(poltype.waitingtime)
            if not os.path.isfile(poltype.outputpath+minboxfilename):
                while not os.path.isfile(poltype.outputpath+boxfilename+'_2'):
                    time.sleep(poltype.waitingtime)
    
                os.rename(poltype.outputpath+boxfilename+'_2',poltype.outputpath+minboxfilename)
    
            alzout='CheckEnergies.alz'
            poltype.CallAnalyze(poltype.outputpath+minboxfilename,key,alzout,poltype.trueanalyzepath,'e')
            poltype.CheckEnergies(alzout)

            if poltype.restrainatomsduringminimization:
                keymods.RemoveKeyWords(poltype,poltype.outputpath+key,['restrain-position'])
    
        for i in range(len(poltype.looseminoutput)):
            output=poltype.looseminoutput[i]
            minboxfilename=poltype.minboxfilename[i]
            boxfilename=poltype.boxfilename[i]
            minpymolboxfilename=poltype.minboxfilenamepymol[i]
            key=poltype.configkeyfilename[i][0]
            if os.path.isfile(poltype.outputpath+minboxfilename) and not os.path.isfile(minpymolboxfilename):
                poltype.PymolReadableFile(minboxfilename,minpymolboxfilename)
    if poltype.minonly==True:
        sys.exit()


def FindTwoAtomsForRestrainingRotation(poltype):
    """
    Intent:
    Input:
    Output:
    Referenced By: 
    Description: 
    """
    t = md.load_arc(poltype.boxfilename[0])
    atomnames='CA'
    indices = t.topology.select('name %s'%(atomnames))
    if len(indices)==0: # dna
        atomnames='C'
        indices = t.topology.select('name %s'%(atomnames))

    indices=[i+1 for i in indices]
    coords=poltype.GrabCoordinates(poltype.boxfilename[0],indices)
    pairs=list(itertools.combinations(coords, 2))
    disttodiffvec={}
    disttoidxpair={} 
    newcoords=[tuple(i) for i in coords]
    coordtoindex=dict(zip(newcoords,indices))
    for pairidx in range(len(pairs)):
        pair=pairs[pairidx]
        progress=(pairidx*100)/len(pairs)
        diff=np.array(pair[0])-np.array(pair[1])
        dist=np.linalg.norm(diff)
        coord1index=coordtoindex[tuple(pair[0])]
        coord2index=coordtoindex[tuple(pair[1])] 
        idxpair=[coord1index,coord2index] 
        disttoidxpair[dist]=idxpair
        disttodiffvec[dist]=diff
    distlist=list(disttodiffvec.keys())
    maxdist=np.amax(np.array(distlist))
    idxpair=disttoidxpair[maxdist]
    return idxpair 
    
