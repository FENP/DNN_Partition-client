#include "making_decision.h"

struct Edge
{
    int from, to;
    float cap, flow;
    Edge(){}
    Edge(int f,int t,float c,float flow):from(f),to(t),cap(c),flow(flow){}
};

// 层号与层结点映射关系
vector<layer> layers;

// 层名与层号对应关系
unordered_map <string, int> name2num;

// 模型各层的DAG图
vector<vector<int>> graph;

// N: 层数 V: 结点数 S: 源点 L: 汇点
int N, V, S, L;

struct Dinic {
    int n,m,s,t;
    vector<Edge> edges;
    vector<vector<int>> G;
    vector<bool> vis;
    vector<int> cur, d;
 
    void init(int n,int s,int t) {
        this->n = n, this->s = s, this->t = t;
        edges.clear();
        G.resize(n, vector<int>(0));
        vis.resize(n, false);
        cur.resize(n, 0);
        d.resize(n, 0);
    }
 
    void AddEdge(int from,int to,float cap) {
        edges.push_back(Edge(from, to, cap, 0));
        edges.push_back(Edge(to, from, 0, 0));
        m = edges.size();
        G[from].push_back(m - 2);
        G[to].push_back(m - 1);
    }
    
    /* 1. 根据网络带宽计算数据传输时间 
     * 2. edge.flow 清零
    */
    void updateEdge(float bandwidth) {
        for(Edge& edge: edges) {
            if(edge.from < N && edge.to != t && edge.cap != 0)
                edge.cap = layers[edge.from].data_size / bandwidth;
            edge.flow = 0;
        }
    }

    /* 填充Edge权重，分别以时间或能耗为衡量指标 */
    void fillEdge(bool is_time) {
        for(Edge& edge: edges) {
            if(edge.from == S) {
                if(is_time)
                    edge.cap = layers[edge.to].execute_time_s;
                else
                    edge.cap = 0;
            }
            else if(edge.to == L) {
                if(is_time)
                    edge.cap = layers[edge.from].execute_time_l;
                else
                    edge.cap = layers[edge.from].energy_consumption;                
            }
        }
    }

    bool BFS() {
        fill(vis.begin(), vis.end(), false);
        queue<int> Q;
        d[s] = 0;
        Q.push(s);
        vis[s] = true;
        while(!Q.empty()) {
            int x = Q.front(); 
            Q.pop();
            for(int i = 0; i < G[x].size(); i++) {
                Edge& e = edges[G[x][i]];
                if(!vis[e.to] && e.cap > e.flow) {
                    vis[e.to] = true;
                    Q.push(e.to);
                    d[e.to] = 1 + d[x];
                }
            }
        }
        return vis[t];
    }
 
    float DFS(int x,float a) {
        if(x == t || a == 0) 
            return a;
        float flow = 0, f;
        for(int& i = cur[x]; i < G[x].size(); i++) {
            Edge& e = edges[G[x][i]];
            if(d[x] + 1 == d[e.to] && (f = DFS(e.to, min(a, e.cap - e.flow))) > 0) {
                e.flow += f;
                edges[G[x][i] ^ 1].flow -= f;
                flow += f;
                a -= f;
                if(a == 0) 
                    break;
            }
        }
        return flow;
    }
 
    float Maxflow() {
        float flow = 0;
        while(BFS()) {
            fill(cur.begin(), cur.end(), 0);
            flow += DFS(s, __FLT_MAX__);
        }
        return flow;
    }

    /* 根据切分决策更新层状态 */
    void getPartitionResult(int option) {
        if(option < 0 || option > 0) {
            for(int i = 1; i < N; i++) {
                if(option < 0)
                    layers[i].status = 0;
                else 
                    layers[i].status = 2;
            }
            layers[0].status = 0;
            if(option > 0) {
                layers[0].status = 1;
            }
        }
        else {
            for(int i = 0; i < N; i++) {
                for(int& j : G[i]) {
                    if(edges[j].cap != 0 && edges[j].cap == edges[j].flow) {
                        if(edges[j].to != t)
                            layers[i].status = 1;
                        else if(layers[i].status < 0)   // 避免状态复写
                            layers[i].status = 0;
                    }
                }
            }
            /* 更新服务端执行的层 */
            for(int& i : G[s]) {
                if(edges[i].cap == edges[i].flow)
                    layers[edges[i].to].status = 2;
            }
        }
    }
}DC;

//模板函数：将string类型变量转换为常用的数值类型 
template <class Type>  
Type stringToNum(const string &str) {  
    istringstream iss(str);  
    Type num;  
    iss >> num;  
    return num;      
}  

void build_graph(ifstream &ifs) {
    graph.resize(N, vector<int>(0));

    string line;
    while (getline(ifs, line)) {
        regex re{' '};
        vector<string> list(sregex_token_iterator(line.begin(), line.end(), re, -1),
            sregex_token_iterator());

        for(int i = 1; i < list.size(); i++) {
            graph[name2num[list[0]]].push_back(name2num[list[i]]);
        }
    }
    S = 0, L = V - 1;
}

void build_layer(ifstream &ifs) {
    string line;
    
    getline(ifs, line);         // 读取头
    while (getline(ifs, line)) {
        regex re{','};
        vector<string> list(sregex_token_iterator(line.begin(), line.end(), re, -1),
            sregex_token_iterator());
        if(list.size() == COLUMN_NUM) {
            layers.push_back(layer(list[0], stringToNum<float>(list[1]), stringToNum<float>(list[3]), \
            stringToNum<float>(list[4]), stringToNum<float>(list[2]), stringToNum<float>(list[5])));
            name2num[list[0]] = N++;
        }
    }

    V = N;
}

/* 对DAG图进行转换 */
void transform_graph() {
    for(int i = 0; i < N; i++) {
        if(graph[i].size() > 1) {
            graph.push_back(vector<int>(graph[i]));
            graph[i].clear();
            graph[i].push_back(V++);
        }
    }

    // 添加源点出边、汇点入边
    S = V++;    // 源点
    graph.push_back(vector<int>(N));
    L = V++;    // 汇点
    graph.push_back(vector<int>(0));
    for(int i = 0; i < N; i++) {
        graph[i].push_back(L);
        graph[S][i] = i;
    }
    
}

/* 初始化DAG图 */
void init_dag(const char* csv_path, const char* dag_path) {
    /* 重置DAG */
    layers.clear();
    graph.clear();
    name2num.clear();
    N = V = 0;

    string csv = csv_path, dag = dag_path;

    // 读取csv文件,得到层结点
    ifstream csv_ifs(csv_path);
    if (!csv_ifs.is_open())
		cout << csv_path << "打开失败" << endl;
    else
        build_layer(csv_ifs);
    csv_ifs.close();

    // 读取DAG文件，构建DAG图
    ifstream dag_ifs(dag_path);
    if (!dag_ifs.is_open())
		cout << dag_path << "打开失败" << endl;
    else
        build_graph(dag_ifs);
    dag_ifs.close();

    // DAG图转换
    transform_graph();

    // 初始化DC
    DC.init(V, S, L);
    // 默认衡量指标为时间
    for(int i = 0; i < V; i++) {
        if(i < N) {
            for(auto& v : graph[i]) {
                if(v != L)
                    DC.AddEdge(i, v, layers[i].data_size);
                else
                    DC.AddEdge(i, v, layers[i].execute_time_l);
            }
        }
        else if(i == S) {
            for(auto& v : graph[i]) {
                DC.AddEdge(i, v, layers[v].execute_time_s);
            }
        }
        else {
            for(auto& v : graph[i]) {
                DC.AddEdge(i, v, __FLT_MAX__);
            }
        }
    }
}

/* 重置层切分状态 */
void resetStatus() {
    for(int i = 0; i < N; i++) {
        layers[i].status = -1;
    }
}

/* 根据网络带宽指定卸载策略 */
void make_partition(float bandwidth) {
    int option = bandwidth > MIN_BANDWIDTH ? (bandwidth < MAX_BANDWIDTH ? 0 : 1) : -1;
    if(option == 0) {
        DC.updateEdge(bandwidth);
        cout << "MaxFlow: " << DC.Maxflow() << endl;
    }

    resetStatus();
    DC.getPartitionResult(option);
}

int getStatus(const char* name) {
    return layers[name2num[name]].status;
}

void display() {
    // 打印转化后的DAG图
    for(int i = 0; i < graph.size(); i++) {
        cout << i << ": ";
        for(auto &num : graph[i])
            cout << num << " ";
        cout << endl;
    }

    // 打印层名及其对应编号
    unordered_map <string, int>::iterator iter;
    for(iter = name2num.begin(); iter != name2num.end(); iter++)
        cout << iter->first<<"\t->\t" << iter->second << endl;

    // 打印各层信息
    cout << setiosflags(ios::fixed);
    cout << setprecision(2);
    for(auto &l : layers) {
        cout << l.name << "\t";
        cout << l.status << "\t";
        cout << l.loading_time << "\t";
        cout << l.data_size << "\t";
        cout << l.execute_time_l << "\t";
        cout << l.execute_time_s << "\t";
        cout << l.energy_consumption << endl;
    }
    cout << defaultfloat;
}

int main() {
    init_dag("./cpu.csv", "./dag");
    make_partition(1);
    display();
    return 0;
}