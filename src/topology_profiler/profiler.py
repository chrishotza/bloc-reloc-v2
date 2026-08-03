import math
import networkx as nx
import pandas as pd

try:
    from networkx.algorithms.community import greedy_modularity_communities
except Exception:
    greedy_modularity_communities=None


class TopologyProfiler:

    def profile(self,G):

        deg=[d for _,d in G.degree()]

        avg_degree=sum(deg)/len(deg)

        degree_std=pd.Series(deg).std()

        max_degree=max(deg)

        hub_ratio=max_degree/avg_degree if avg_degree else 0

        gini=self.gini(deg)

        clustering=nx.average_clustering(G)

        transitivity=nx.transitivity(G)

        try:
            assortativity=nx.degree_assortativity_coefficient(G)
        except Exception:
            assortativity=float("nan")

        try:
            core=max(nx.core_number(G).values())
        except Exception:
            core=float("nan")

        try:
            largest=max(nx.connected_components(G),key=len)
            H=G.subgraph(largest)

            diameter=nx.diameter(H)
            avg_path=nx.average_shortest_path_length(H)
        except Exception:
            diameter=float("nan")
            avg_path=float("nan")

        algebraic=float("nan")

        spectral=float("nan")

        modularity=float("nan")
        communities=float("nan")

        if greedy_modularity_communities is not None:
            try:
                comm=list(greedy_modularity_communities(G))
                communities=len(comm)
                modularity=nx.algorithms.community.modularity(G,comm)
            except Exception:
                pass

        return {

            "nodes":G.number_of_nodes(),

            "edges":G.number_of_edges(),

            "density":nx.density(G),

            "avg_degree":avg_degree,

            "degree_std":degree_std,

            "max_degree":max_degree,

            "hub_ratio":hub_ratio,

            "degree_gini":gini,

            "clustering":clustering,

            "transitivity":transitivity,

            "assortativity":assortativity,

            "core_number":core,

            "diameter":diameter,

            "avg_path":avg_path,

            "spectral_radius":spectral,

            "algebraic_connectivity":algebraic,

            "communities":communities,

            "modularity":modularity
        }

    def gini(self,x):

        x=sorted(x)

        n=len(x)

        s=sum(x)

        if s==0:
            return 0.0

        acc=0

        for i,v in enumerate(x,1):
            acc+=i*v

        return (2*acc)/(n*s)-(n+1)/n
