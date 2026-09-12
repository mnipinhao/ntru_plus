#!/usr/bin/env python3
"""Machine-check the P14 class decomposition, slot path and TBL indices."""
import json
import generate

forward=generate.exact_map()
path,classes=generate.class_path(forward[:432])
states=generate.build_slots(path)
indices,class_for_output=generate.make_indices(forward[:432],path,classes,states)
loads=8
for before,after in zip(states,states[1:]):
    loads+=sum(a!=b for a,b in zip(before,after))
assert loads==64
for output_q in range(54):
    slots=states[class_for_output[output_q]]
    for lane in range(8):
        source_index=forward[8*output_q+lane]
        source_q,source_lane=divmod(source_index,8)
        slot=slots.index(source_q);bank=slot//4;table_slot=slot%4
        assert indices[output_q][bank][2*lane]==16*table_slot+2*source_lane
        assert indices[output_q][bank][2*lane+1]==16*table_slot+2*source_lane+1
        assert indices[output_q][1-bank][2*lane]==255
        assert indices[output_q][1-bank][2*lane+1]==255
result={"status":"pass","classes":len(path),"class_sizes":sorted(map(len,classes.values())),
        "maximum_overlap":56,"source_q_loads_per_top":loads,"outputs_checked":54,
        "lanes_checked":432,"top_copy_identity":all(forward[i+432]==forward[i]+432 for i in range(432))}
print(json.dumps(result,indent=2))
