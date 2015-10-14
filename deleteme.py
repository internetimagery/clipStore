from pprint import pprint
# Testing inclusion / Exclusion
clipData = {u'pCube1': {u'rotateX': [-43.7568480395646],
             u'rotateY': [36.32400319749655],
             u'rotateZ': [-9.682797904684499],
             u'translateX': [0.0],
             u'translateY': [0.0],
             u'translateZ': [0.0]}}
selection = {u'pCube1': {u'rotateX': True,
             u'rotateY': True,
             u'rotateZ': True,
             u'scaleX': True,
             u'scaleY': True,
             u'scaleZ': True,
             u'translateX': [0.0],
             u'translateY': [0.0],
             u'translateZ': True,
             u'visibility': True}}
# include
# p = dict( (a, dict( (c, clipData[a][c]) for c, d in b.items() if c in clipData[a] ) ) for a, b in selection.items() if a in clipData )
# exclude
p = dict( (e, f) for e, f in dict( (a, dict( (c, d) for c, d in b.items() if a not in selection or c not in selection[a] ) ) for a, b in clipData.items() ).items() if f)

pprint(p)

            # clipData = dd(dict)
            # for o, attrs in clipData.items():
            #     for at in attrs:
            #         if o not in selection or at not in selection[o]:
            #             clipData[o][at] = clipData[o][at]
