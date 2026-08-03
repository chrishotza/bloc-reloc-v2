import math
import random
from collections import Counter

class BlocRelocV2:

    def __init__(self, graph, k=4, seed=42, variant="baseline", operator="1_swap"):
        self.graph=graph
        self.k=k
        self.seed=seed
        self.variant=variant
        self.operator=operator
        random.seed(seed)
        self.degree=dict(graph.degree())

    def initialize_partition(self):
        return {n:i%self.k for i,n in enumerate(self.graph.nodes())}

    def decision_cost(self,u,v):
        if self.variant=="baseline":
            return 1.0

        if self.variant=="affinity_modified":
            return 1.0/math.sqrt(self.degree[u]*self.degree[v]+1.0)

        return 1.0

    def weighted_cut(self,p):
        c=0.0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                c+=self.decision_cost(u,v)
        return c

    def edge_cut(self,p):
        cut=0
        for u,v in self.graph.edges():
            if p[u]!=p[v]:
                cut+=1
        return cut


    def two_swap_step(self, part, counts, best, max_samples=None):

        accepted=0
        rejected=0

        nodes=list(self.graph.nodes())

        if max_samples is None:

            random.shuffle(nodes)

            pairs=[]

            for i in range(len(nodes)):
                for j in range(i+1,len(nodes)):
                    pairs.append((nodes[i],nodes[j]))

        else:

            pairs=[
                tuple(random.sample(nodes,2))
                for _ in range(max_samples)
            ]

        for u,v in pairs:

            if part[u]==part[v]:
                continue

            bu=part[u]
            bv=part[v]

            part[u]=bv
            part[v]=bu

            c=self.weighted_cut(part)

            if c<best:
                best=c
                accepted+=1
            else:
                part[u]=bu
                part[v]=bv
                rejected+=1

        return part,counts,best,accepted,rejected

    def refine(self,iterations=50,hybrid_period=None,hybrid_samples=1200,reactive_stall=None):

        part=self.initialize_partition()
        counts=Counter(part.values())

        target=len(part)/self.k
        tolerance=max(1,int(target*0.05))

        best=self.weighted_cut(part)

        trace=[]

        stall_counter=0

        for it in range(iterations):

            accepted=0
            rejected=0

            nodes=list(self.graph.nodes())
            random.shuffle(nodes)

            for node in nodes:

                old=part[node]
                best_block=old
                best_cut=best

                for b in range(self.k):

                    if b==old:
                        continue

                    if counts[b]+1 <= target+tolerance and counts[old]-1 >= target-tolerance:

                        part[node]=b

                        c=self.weighted_cut(part)

                        if c<best_cut:
                            best_cut=c
                            best_block=b
                            accepted+=1
                        else:
                            rejected+=1

                        part[node]=old

                if best_block!=old:
                    counts[old]-=1
                    counts[best_block]+=1

                part[node]=best_block

                if best_cut<best:
                    stall_counter=0
                else:
                    stall_counter+=1

                best=best_cut

            if (
                hybrid_period is not None
                and hybrid_period>0
                and (it+1)%hybrid_period==0
            ):

                part,counts,best,a2,r2=self.two_swap_step(
                    part,
                    counts,
                    best,
                    max_samples=hybrid_samples
                )

                accepted+=a2
                rejected+=r2

                stall_counter=0

            elif (
                reactive_stall is not None
                and stall_counter>=reactive_stall
            ):

                part,counts,best,a2,r2=self.two_swap_step(
                    part,
                    counts,
                    best,
                    max_samples=hybrid_samples
                )

                accepted+=a2
                rejected+=r2

                stall_counter=0

            trace.append({
                "iteration":it,
                "weighted_cost":best,
                "edge_cut":self.edge_cut(part),
                "accepted":accepted,
                "rejected":rejected
            })

        return {
            "partition":part,
            "edge_cut":self.edge_cut(part),
            "weighted_cost":best,
            "trace":trace
        }
