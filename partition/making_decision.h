#ifndef MAKING_DECISION
#define MAKING_DECISION

#include <iostream>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <unordered_map>
#include <vector>
#include <string>
#include <regex>
#include <queue>

using namespace std;

#define COLUMN_NUM 6    // csv文件列数
#define MIN_BANDWIDTH 0         // 最小带宽，小于等于此值将直接选择在本地推理
#define MAX_BANDWIDTH 10000     // 最大带宽，大于等于此值将直接选择在边缘推理

struct layer {
    string name;
    int status;             // 层切分状态（0：本地执行；1：本地执行且输出结果；2：边缘执行）
    float loading_time;     // 初始化时间（ms）
	float execute_time_l;   // 本地执行时间（ms）
    float execute_time_s;   // 服务端执行时间（ms）
    float data_size;        // 输出数据大小（MB）
    float energy_consumption;// 本地执行能耗
	layer(string _name, float _loading_time, float _execute_time_l, float _execute_time_s, float _data_size, \
    float _energy_consumption): \
    name(_name), loading_time(_loading_time), execute_time_l(_execute_time_l), execute_time_s(_execute_time_s), \
    data_size(_data_size), energy_consumption(_energy_consumption), status(-1){}
	layer(){}
};

extern "C"{
    /* 初始化DAG图 
     * csv_path: 模型各层参数的路径
     * dag_path: 模型DAG路径
    */
    void init_dag(const char* csv_path, const char* dag_path);
    
    /* 执行切分决策 
     * bandwidth: 网络带宽
    */
    void make_partition(float bandwidth);

    /* 获取层切分状态
     * name: 层名
     * 返回值：层切分状态（0：本地执行；1：本地执行且输出结果；2：边缘执行）
    */
    int getStatus(const char* name);

    /* 更新优化目标
     * is_time: true表示优化时间；false表示优化客户端能耗
    */
    void transform_target(bool is_time);

    /* 打印结点与DAG */
    void display();
}

#endif