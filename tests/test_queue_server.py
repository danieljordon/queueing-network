import numpy as np
import queueing_tool  as qt
import graph_tool.all as gt
import unittest


class TestQueueServers(unittest.TestCase) :

    def setUp(self) :
        self.lam = np.random.randint(1,10) + 0.0
        self.rho = np.random.uniform(0.5, 1)


    def test_QueueServer_accounting(self) :

        nSe = np.random.randint(1, 10)
        mu  = self.lam / (self.rho * nSe)
        arr = lambda t : t + np.random.exponential(1/self.lam)
        ser = lambda t : t + np.random.exponential(1 / mu)

        q   = qt.QueueServer(nServers=nSe, arrival_f=arr, service_f=ser)
        q.set_active()
        nEvents = 15000
        
        ans = np.zeros((nEvents,3), bool)

        for k in range(nEvents) :
            nt = len(q._departures) + len(q._queue) + len(q._arrivals) - 2
            nS = len(q._departures) + len(q._queue) - 1
            ans[k,0] = nt == q._nTotal
            ans[k,1] = nS == q.nSystem
            ans[k,2] = len(q._departures) - 1 <= q.nServers
            q.simulate(n=1)

        self.assertTrue( ans.all() )


    def test_QueueServer_simulation(self) :

        nSe = np.random.randint(1, 10)
        mu  = self.lam / (self.rho * nSe)
        arr = lambda t : t + np.random.exponential(1/self.lam)
        ser = lambda t : t + np.random.exponential(1 / mu)

        q   = qt.QueueServer(nServers=nSe, arrival_f=arr, service_f=ser)
        q.set_active()
        nEvents = 5000
        
        ans = np.zeros(4, bool)

        k   = np.random.randint(nEvents * 0.75, nEvents * 1.25)
        nA0 = q._oArrivals
        nD0 = q.nDepartures
        q.simulate(n=k)
        ans[0] = q.nDepartures + q._oArrivals - nA0 - nD0 == k

        k   = np.random.randint(nEvents * 0.75, nEvents * 1.25)
        nA0 = q._oArrivals
        q.simulate(nA=k)
        ans[1] = q._oArrivals - nA0 == k

        k   = np.random.randint(nEvents * 0.75, nEvents * 1.25)
        nD0 = q.nDepartures
        q.simulate(nD=k)
        ans[2] = q.nDepartures - nD0 == k

        t  = 100 * np.random.uniform(0.5, 1)
        t0 = q.current_time
        q.simulate(t=t)
        ans[3] = q.current_time - t0 >= t

        self.assertTrue( ans.all() )


    def test_LossQueue_accounting(self) :

        nSe = np.random.randint(1, 10)
        mu  = self.lam / (self.rho * nSe)
        arr = lambda t : t + np.random.exponential(1/self.lam)
        ser = lambda t : t + np.random.exponential(1 / mu)

        q   = qt.LossQueue(nServers=nSe, arrival_f=arr, service_f=ser)
        q.set_active()
        nEvents = 15000
        
        ans = np.zeros((nEvents,3), bool)

        for k in range(nEvents) :
            nt = len(q._departures) + len(q._queue) + len(q._arrivals) - 2
            nS = len(q._departures) + len(q._queue) - 1
            ans[k,0] = nt == q._nTotal
            ans[k,1] = nS == q.nSystem
            ans[k,2] = len(q._departures) - 1 <= q.nServers
            q.simulate(n=1)

        self.assertTrue( ans.all() )


    def test_LossQueue_blocking(self) :

        nSe = np.random.randint(1, 10)
        mu  = self.lam / (self.rho * nSe)
        k   = np.random.randint(5, 15)
        scl = 1 / (mu * k)

        arr = lambda t : t + np.random.exponential(1/self.lam)
        ser = lambda t : t + np.random.gamma(k, scl)

        q  = qt.LossQueue(nServers=nSe, arrival_f=arr, service_f=ser)
        q.set_active()
        nE = 500
        c  = 0
        ans = np.zeros(nE, bool)

        while c < nE :
            if q.next_event_description() == 1 and q.at_capacity() :
                nB0 = q.nBlocked
                q.simulate(n=1)
                ans[c] = nB0 + 1 == q.nBlocked
                c += 1
            else :
                q.simulate(n=1)

        tmp = np.ones(5)
        self.assertTrue( ans.all() )


    def test_ResourceQueue_network(self) :

        nV  = 100
        ps  = np.random.uniform(0, 5, size=(nV, 2))

        g, pos = gt.geometric_graph(ps, 1)
        q_cls = {1 : qt.ResourceQueue, 2 : qt.ResourceQueue}
        q_arg = {1 : {'nServers' : 50}, 2 : {'nServers' : 500}}

        qn  = qt.QueueNetwork(g, q_classes=q_cls, q_args=q_arg)
        qn.max_agents = 400000
        qn.initialize(queues=range(g.num_edges()))
        qn.simulate(n=50000)

        nServ = {1 : 50, 2 : 500}
        ans   = np.array([q.nServers != nServ[q.edge[3]] for q in qn.edge2queue])
        self.assertTrue( ans.any() )


    def test_InfoQueue_network(self) :

        nV  = 100
        ps  = np.random.uniform(0, 5, size=(nV, 2))

        g, pos = gt.geometric_graph(ps, 1)
        q_cls = {1 : qt.InfoQueue}
        q_arg = {1 : {'net_size' : g.num_edges()} }

        qn  = qt.QueueNetwork(g, q_classes=q_cls, q_args=q_arg, seed=17)
        qn.max_agents = 40000
        qn.initialize(queues=range(g.num_edges()))
        qn.simulate(n=2000)

        # Finish this
        self.assertTrue( True )


if __name__ == '__main__':
    unittest.main()