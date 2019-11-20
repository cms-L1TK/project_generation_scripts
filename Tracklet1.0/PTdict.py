L3F3F5_ins = ["F1D5L1D4_F5","F1D5F2D5_F5","F3D5F4D5_F5",
              "L1D3L2D4_F3","L1D4L2D4_F3","F1D5L1D4_F3","F1D5F2D5_F3",
              "L1D3L2D3_L3","L1D3L2D4_L3","L1D4L2D4_L3","L5D3L6D3_L3","L5D3L6D4_L3","L5D4L6D4_L3","1'b0","1'b0","1'b0","1'b0","1'b0","1'b0","1'b0"]
L3F3F5_outs = {"L3D3_L1L2":"projout_layer_1","L3D4_L1L2":"projout_layer_2","L3D3_L5L6":"projout_layer_3","L3D4_L5L6":"projout_layer_4",
               "F3D5_F1F2":"projout_disk_1","F3D6_F1F2":"projout_disk_2","F5D5_F1F2":"projout_disk_3","F5D6_F1F2":"projout_disk_4","F5D5_F3F4":"projout_disk_5","F5D6_F3F4":"projout_disk_6"}

L2L4F2_ins = ["L1D3L2D4_F2","L1D4L2D4_F2","L3D4L4D4_F2","F1D5L1D4_F2","F3D5F4D5_F2","1'b0","1'b0",
              "L1D3L2D3_L4","L1D3L2D4_L4","L1D4L2D4_L4","L5D3L6D3_L4","L5D3L6D4_L4","L5D4L6D4_L4","L3D3L4D3_L2","L3D3L4D4_L2","L3D4L4D4_L2","L5D3L6D3_L2","L5D3L6D4_L2","L5D4L6D4_L2","F1D5F2D5_L2"]
L2L4F2_outs = {"L2D3_L3L4":"projout_layer_1","L2D4_L3L4":"projout_layer_2","L4D3_L1L2":"projout_layer_3","L4D4_L1L2":"projout_layer_4","L2D3_L5L6":"projout_layer_5","L4D3_L5L6":"projout_layer_6","L2D4_L5L6":"projout_layer_7","L4D4_L5L6":"projout_layer_8",
               "F2D5_F3F4":"projout_disk_1","F2D6_F3F4":"projout_disk_2"}

F1L5_ins = ["L1D3L2D3_F1","L1D3L2D4_F1","L1D4L2D4_F1","L3D4L4D4_F1","F3D5F4D5_F1","1'b0","1'b0",
            "L1D3L2D3_L5","L1D3L2D4_L5","L1D4L2D4_L5","L3D3L4D3_L5","L3D3L4D4_L5","L3D4L4D4_L5","1'b0","1'b0","1'b0","1'b0","1'b0","1'b0","1'b0"]
F1L5_outs = {"L5D3_L3L4":"projout_layer_1","L5D4_L3L4":"projout_layer_2","L5D3_L1L2":"projout_layer_3","L5D4_L1L2":"projout_layer_4",
             "F1D5_F3F4":"projout_disk_1","F1D6_F3F4":"projout_disk_2"}

L1L6F4_ins = ["L1D3L2D4_F4","L1D4L2D4_F4","F1D5L1D4_F4","F1D5F2D5_F4","1'b0","1'b0","1'b0",
              "L1D3L2D3_L6","L1D3L2D4_L6","L1D4L2D4_L6","L3D3L4D3_L6","L3D3L4D4_L6","L3D4L4D4_L6","L3D3L4D3_L1","L3D3L4D4_L1","L3D4L4D4_L1","L5D3L6D3_L1","L5D3L6D4_L1","L5D4L6D4_L1","F1D5F2D5_L1"]
L1L6F4_outs = {"L1D3_L3L4":"projout_layer_1","L6D3_L3L4":"projout_layer_2","L1D4_L3L4":"projout_layer_3","L6D4_L3L4":"projout_layer_4","L6D3_L1L2":"projout_layer_5","L6D4_L1L2":"projout_layer_6","L1D3_L5L6":"projout_layer_7","L1D4_L5L6":"projout_layer_8",
               "F4D5_F1F2":"projout_disk_1","F4D6_F1F2":"projout_disk_2"}
