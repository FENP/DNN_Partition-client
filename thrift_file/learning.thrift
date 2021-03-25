namespace py learning

service  collaborativeIntelligence {
    void partition(1:map<string, i8> partitionResult)
    i32 inference(1:map<string ,binary> middleResult)
}