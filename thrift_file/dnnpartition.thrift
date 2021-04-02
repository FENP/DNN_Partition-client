namespace py dnnpartition

service  collaborativeIntelligence {
    void partition(1:map<string, i8> partitionResult)
    binary inference(1:map<string ,binary> middleResult)
}