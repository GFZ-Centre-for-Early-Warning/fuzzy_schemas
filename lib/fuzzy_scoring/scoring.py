#scoring.py 
#atuthor: Massimiliano Pittore, @GFZ 2019
#

import pandas as pd
import yaml
import json
import os
import seaborn as sns
import matplotlib.pyplot as plt

from fuzzy import defuzzify, fuzzy_sum, fuz_argmax

# function that computes the score of a building for a building type
def compute_single_bscore_fuzzy(bdg,btype,wgsScheme, bmodScheme,fuzcompScheme, bDefuz=False, defuzMode='mode'):
    '''
    Computes the fuzzy score of a single building 'bdg'
    against a reference  building type 'btype'
    , according to a specific weighting scheme wgs_scheme'
    and a building definition scheme 'bmod_scheme'. 
    
    Also needs the definition 
    of a set of fuzzy compatbility levels 'fuzcompScheme'. If the booleab 'bDefuz' is True 
    then a crisp value is returned as score according to the defuzzifcation mode 'defuzMode'.
    The default compatibility value for attribute values not included in the
    class definition schema is '0' (neutral).
    The height is automtically considered as a constraint. If the constraint is not 
    verified, the final score is set to '---' (highly incompatible).
    '''
    #compute the compatibility score. Default comp value is '0', i.e. neutral
    s=[0,0,0]
    for k in wgsScheme.keys():
        a = fuzcompScheme[bmodScheme[btype][k].get(bdg[k],'0')]
        s = fuzzy_sum(s,a,1,wgsScheme[k])
    
    #check the additional attribute, in this case the height
    ch1 = True
    if (bdg['height_1'] != 'NO_DATA'):
        cs1 = ((bdg['height_1'] >= bmodScheme[btype]['height_1']['H_MIN']) & 
               (bdg['height_1'] <= bmodScheme[btype]['height_1']['H_MAX']))
    
    #apply the constraint. 
    #if the constraint is not fulfilled the resulting
    #score is set to 'highly incompatible'
    if (cs1 == False):
        s= fuzcompScheme['---']

    if bDefuz:
        score = defuzzify(s,defuzMode)
        return score
    else:
        return s

def compute_bscore_fuzzy(bdg, wgsScheme, bmodScheme,fuzcompScheme,bDefuz=False, defuzMode='mode'):
    '''
    Computes the scores for the building 'bdg', against all building 
    types defined in the class definition scheme 'bmodScheme'.
    Also needs the definition of a set of fuzzy compatbility levels 'fuzcompScheme'. 
    If the booleab 'bDefuz' is True then a crisp value is returned as score 
    according to the defuzzifcation mode 'defuzMode'.
    The default compatibility value for attribute values not included in the
    class definition schema is '0' (neutral).
    The height is automtically considered as a constraint. If the constraint is not 
    verified, the final score is set to '---' (highly incompatible).
    '''
    res={}
    for bt in bmodScheme.keys():
        res[bt]=compute_single_bscore_fuzzy(bdg,bt, wgsScheme, bmodScheme,fuzcompScheme,bDefuz,defuzMode) 
        res['object_id']=bdg['object_id']
    return res

def compute_expo_model_fuzzy(bdgs_set, wgsScheme, bmodScheme, fuzcompScheme, bFilterScore = True,bFilterScoreThreshold = 0, bDefuz=False, defuzMode='mode'):
    '''
    Applies the fuzzy scoring defined by the components 'wgs_schema','bmod_schema'
    to the buildings set 'bdgs_set'. 
    Returns the final exposure model and separately the scores for all
    buildings in 'bdgs_set'.
    if 'bFilterScore' is set to True, the 'not Valid' buildings (i.e., those whose fuzzy 
    score is smaller than 'bFilterScoreThreshold') are associated 
    to the 'OTH' building type.
    
    Returns the input buildings set with the respective assigned class, 
    and an additional dataframe with all the scores of the buildings with respect
    to the classes defined by the class definition scheme.
    '''
    #compute the score for each building in the dataframee
    scores = pd.DataFrame([compute_bscore_fuzzy(b, wgsScheme, bmodScheme,fuzcompScheme,False, defuzMode) for i,b in bdgs_set.iterrows()])
    
    # assign to each building the argmax of the score and 
    # set a flag to 'true' for the buildings whose best score is >= threshold
    if (bDefuz):
        scores['btype']=scores[bmodScheme.keys()].idxmax(1)
        scores['valid'] = scores.apply(lambda df:df[df['btype']]>bFilterScoreThreshold, 1)
    else:
        scores['btype'] = [bmodScheme.keys()[fuz_argmax(x.tolist())] 
             for ind,x in scores[bmodScheme.keys()].iterrows()]
        scores['valid'] = scores.apply(lambda df:defuzzify(df[df['btype']])>bFilterScoreThreshold, 1)

    #select only the valid ones ?
    if (bFilterScore):
        #the building type 'OTH' groups all the entries whose assignment was invalid
        for it, bd in scores[scores['valid']==False].iterrows():
            scores.set_value(it,'btype','OTH')
            bd['btype']='OTH'

    expo_df = pd.merge(bdgs_set,scores[['object_id','btype']], how='inner', on='object_id')
    return expo_df,scores


def create_bmod_matrix(bmodScheme,wgsScheme,fuzcompScheme):
    '''
    Auxiliary funtion. 
    Creates a matrix with as many rows
    as the defined building types, and as many columns as
    the number of the attribute values explicitly rated in terms
    of compatibility value. The compatibility values 
    are defuzzified using the 'mode' to be colormapped accordingly.
    '''
    bmod_mat = pd.DataFrame(columns=['btype','attribute_type','attribute_val','score'])
    for bt in bmodScheme.keys():
        for k in wgsScheme.keys():
            for av in bmodScheme[bt][k]:
                a = fuzcompScheme[bmodScheme[bt][k][av]]
                s= defuzzify(a,'mode')
                bmod_mat = bmod_mat.append({'btype':bt, 
                                            'attribute_type':k,
                                'attribute_val':'{} : {}'.format(k,av),
                                                               'score':s},ignore_index=True)
            
    bmod_mat['score'] = pd.to_numeric(bmod_mat['score'])
    return bmod_mat

def plot_bclass_schema(bmodScheme, wgsScheme,fuzcompScheme,figfilename=''):
    '''
    Plots the class definition scheme 'bmodScheme' in form of a matrix with as many rows
    as the defined building types, and as many columns as
    the number of the attribute values explicitly rated in terms
    of compatibility value. The defuzzified compatibility value (as mode)
    is shown with a colormap.
    Uses the auxiliary function 'create_bmod_matrix'.
    '''
    bmod_mat = create_bmod_matrix(bmodScheme,wgsScheme,fuzcompScheme)
    bmod_mat_piv = bmod_mat.pivot('btype','attribute_val','score')
    f, ax = plt.subplots(figsize=(18, 8))
    sns.heatmap(bmod_mat_piv,vmin=-1, vmax=1,
                cmap=sns.color_palette("coolwarm", 7),linecolor='gray',
                    linewidth=0.1,xticklabels=1,ax=ax)
    if (figfilename):
        print 'saving fig {}'.format(figfilename)
        plt.tight_layout()
        plt.savefig(figfilename,dpi=300)
        plt.show()
    plt.show()

def exportClassDict(classdict,filename, output_format = 'json'):
    '''
    Exports a class definition schema (in form of a dictionary) into a text file. 
    possible extensions are '.json' and '.yml' / '.yaml'
    '''
    pre, ext = os.path.splitext(filename)
    if (output_format == 'json'):
        output = json.dumps(classdict)
        filename=pre+'.json'
    elif (output_format == 'yaml') | (output_format == 'yml'):
        output = yaml.dump(classdict, default_flow_style=False, explicit_start=True)
        filename=pre+'.yml'
    else:
        raise NameError('unrecognized output_format: {}'.format(output_format))
    outf = open(filename,'w')
    outf.write(output)
    outf.close()

def importClassDict(filename):
    '''
    import a class definition schema into a dictionary. 
    possible extensions are '.json' and '.yml' / '.yaml'
    '''
    pre, ext = os.path.splitext(filename)
    inf = open(filename,'r')

    if ((ext == '.yml') | (ext == '.yaml')):
        cdict = yaml.load(inf.read())
    elif (ext == '.json'):
        cdict = json.loads(inf.read(), object_pairs_hook=OrderedDict)
    else:
        inf.close()
        raise NameError('Unrecognized extension: {}'.format(ext))
    inf.close()
    return cdict
