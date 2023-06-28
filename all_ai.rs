use std::collections::{HashMap, HashSet};
use std::hash::Hash;
use std::cmp::PartialOrd;
use std::ops::Add;
use std::iter::FromIterator;

type Node = usize;
type Edge = usize;
type Domain = f64;
type Cycle = Vec<Edge>;

struct NegCycleFinder<Node, Edge, Domain> {
    pred: HashMap<Node, (Node, Edge)>,
    digraph: HashMap<Node, HashMap<Node, Edge>>,
}

impl<Node, Edge, Domain> NegCycleFinder<Node, Edge, Domain>
where
    Node: Eq + Hash + Clone,
    Edge: Eq + Hash + Clone,
    Domain: PartialOrd + Add<Output = Domain> + Default + Copy,
{
    fn new(gra: HashMap<Node, HashMap<Node, Edge>>) -> Self {
        NegCycleFinder {
            pred: HashMap::new(),
            digraph: gra,
        }
    }

    fn find_cycle(&mut self) -> Option<Cycle> {
        let mut visited: HashMap<Node, Node> = HashMap::new();
        for vtx in self.digraph.keys().filter(|vtx| !visited.contains_key(vtx)) {
            let mut utx = vtx.clone();
            loop {
                visited.insert(utx.clone(), vtx.clone());
                if !self.pred.contains_key(&utx) {
                    break;
                }
                let (next, _) = self.pred[&utx].clone();
                if visited.contains_key(&next) {
                    if visited[&next] == *vtx {
                        return Some(next);
                    }
                    break;
                }
                utx = next;
            }
        }
        None
    }

    fn relax(
        &mut self,
        dist: &mut HashMap<Node, Domain>,
        get_weight: &dyn Fn(&Edge) -> Domain,
    ) -> bool {
        let mut changed = false;
        for (utx, nbrs) in &self.digraph {
            for (vtx, edge) in nbrs {
                let distance = dist[utx] + get_weight(edge);
                if dist[vtx] > distance {
                    dist.insert(vtx.clone(), distance);
                    self.pred.insert(vtx.clone(), (utx.clone(), edge.clone()));
                    changed = true;
                }
            }
        }
        changed
    }

    fn howard(
        &mut self,
        dist: &mut HashMap<Node, Domain>,
        get_weight: &dyn Fn(&Edge) -> Domain,
    ) -> Option<Cycle> {
        self.pred.clear();
        while self.relax(dist, get_weight) {
            if let Some(vtx) = self.find_cycle() {
                return Some(self.cycle_list(&vtx));
            }
        }
        None
    }

    fn cycle_list(&self, handle: &Node) -> Cycle {
        let mut vtx = handle.clone();
        let mut cycle = Vec::new();
        loop {
            let (utx, edge) = self.pred[&vtx].clone();
            cycle.push(edge);
            vtx = utx;
            if vtx == *handle {
                break;
            }
        }
        cycle
    }

    fn is_negative(
        &self,
        handle: &Node,
        dist: &HashMap<Node, Domain>,
        get_weight: &dyn Fn(&Edge) -> Domain,
    ) -> bool {
        let mut vtx = handle.clone();
        loop {
            let (utx, edge) = self.pred[&vtx].clone();
            if dist[&vtx] > dist[&utx] + get_weight(&edge) {
                return true;
            }
            vtx = utx;
            if vtx == *handle {
                break;
            }
        }
        false
    }
}

struct ParametricAPI<Node, Edge, Ratio> {
    distance: Box<dyn Fn(Ratio, &Edge) -> Ratio>,
    zero_cancel: Box<dyn Fn(&Cycle) -> Ratio>,
}

impl<Node, Edge, Ratio> ParametricAPI<Node, Edge, Ratio> {
    fn new(
        distance: Box<dyn Fn(Ratio, &Edge) -> Ratio>,
        zero_cancel: Box<dyn Fn(&Cycle) -> Ratio>,
    ) -> Self {
        ParametricAPI {
            distance,
            zero_cancel,
        }
    }
}

struct MaxParametricSolver<Node, Edge, Ratio> {
    ncf: NegCycleFinder<Node, Edge, Ratio>,
    omega: ParametricAPI<Node, Edge, Ratio>,
}

impl<Node, Edge, Ratio> MaxParametricSolver<Node, Edge, Ratio>
where
    Node: Eq + Hash + Clone,
    Edge: Eq + Hash + Clone,
    Ratio: PartialOrd + Default + Copy,
{
    fn new(
        gra: HashMap<Node, HashMap<Node, Edge>>,
        omega: ParametricAPI<Node, Edge, Ratio>,
    ) -> Self {
        MaxParametricSolver {
            ncf: NegCycleFinder::new(gra),
            omega,
        }
    }

    fn run(
        &mut self,
        dist: &mut HashMap<Node, Domain>,
        ratio: Ratio,
    ) -> (Ratio, Cycle) {
        let mut r_min = ratio;
        let mut c_min = Cycle::new();
        let mut cycle = Cycle::new();

        loop {
            if let Some(ci) = self.ncf.howard(dist, &|edge| (self.omega.distance)(ratio, edge)) {
                let ri = (self.omega.zero_cancel)(&ci);
                if r_min > ri {
                    r_min = ri;
                    c_min = ci;
                }
            } else {
                break;
            }
            if r_min >= ratio {
                break;
            }
            cycle = c_min.clone();
            ratio = r_min;
        }

        (ratio, cycle)
    }
}

fn set_default(gra: &mut HashMap<Node, HashMap<Node, HashMap<String, Domain>>>, weight: &str, value: Domain) {
    for (_, nbrs) in gra {
        for (_, e) in nbrs {
            e.entry(weight.to_string()).or_insert(value);
        }
    }
}

struct CycleRatioAPI<Node, Ratio> {
    gra: HashMap<Node, HashMap<Node, HashMap<String, Domain>>>,
    k: Ratio,
}

impl<Node, Ratio> CycleRatioAPI<Node, Ratio>
where
    Node: Eq + Hash + Clone,
    Ratio: PartialOrd + Default + Copy,
{
    fn new(gra: HashMap<Node, HashMap<Node, HashMap<String, Domain>>>, k: Ratio) -> Self {
        CycleRatioAPI { gra, k }
    }

    fn distance(&self, ratio: Ratio, edge: &HashMap<String, Domain>) -> Ratio {
        self.k * edge["cost"] - ratio * edge["time"]
    }

    fn zero_cancel(&self, cycle: &Cycle) ->
