from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
import tensorflow as tf
from scipy import misc
import cv2
import numpy as np
from .facenet import load_model, to_rgb, flip, prewhiten
from .detect_face import detect_face, create_mtcnn
import os
import time
import pickle
import json
import logging
import datetime
import sys
from .celebrity_dictionary import dic

path = "identify/face_recognition/"
input_video_dir = path + "video/"
modeldir = path + 'model/20170511-185253.pb'
# classifier_filename = path + 'class/classifier.pkl'
# train_img = path + "train_img"

def identify_video_main(input_video, target_name):
    logging.info("=== start to identify %s %s ===", input_video, target_name)
    a = datetime.datetime.now()
    input_video = input_video_dir + input_video
    results = identify_video(input_video, target_name)
    logging.info("=== finish identifying ===")
    b = datetime.datetime.now()
    print(b-a)
    logging.info("identifying time period: %s", str(b-a))
    return results

def identify_video(input_video, target_name):
    classifier_filename = path + 'class/' + dic[target_name] + '.pkl'
    npy = path + 'npy'
    train_img = path + "train_img/" + dic[target_name]

    with tf.Graph().as_default():
        gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
        sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
        with sess.as_default():
            pnet, rnet, onet = create_mtcnn(sess, npy)

            minsize = 20  # minimum size of face
            threshold = [0.6, 0.7, 0.7]  # three steps's threshold
            factor = 0.709  # scale factor
            margin = 44
            frame_interval = 3
            batch_size = 1000
            image_size = 182
            input_image_size = 160

            HumanNames = os.listdir(train_img)
            if '.DS_Store' in HumanNames:
                HumanNames.remove('.DS_Store')
            HumanNames.sort()

            print('Loading Modal')
            load_model(modeldir)
            images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
            embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
            phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
            embedding_size = embeddings.get_shape()[1]

            classifier_filename_exp = os.path.expanduser(classifier_filename)
            # modified
            with open(classifier_filename_exp, 'rb') as infile:
                (model, class_names) = pickle.load(infile, encoding='latin-1')

            video_capture = cv2.VideoCapture(input_video)
            c = 0

            print('Start Recognition')
            prevTime = 0

            # new
            frame_gap = 0
            appearance_time = []
            result = {}
            result.setdefault('appearance_time',[])
            last_appearance = False
            last_last_appearance = False
            while True:
                # new
                frame_gap += 1
                ret, frame = video_capture.read()
                # new
                # 每10帧做一次人脸识别，约0.3秒间隔
                if frame_gap % 10 != 1:
                    continue
                # new
                if ret is False and last_appearance:
                    appearnace = {}
                    appearnace["target_name"] = result_names
                    appearnace["start_time"] = start_time
                    appearnace["end_time"] = end_time
                    result['appearance_time'].append(appearnace)
                    appearance_time.append([start_time, timestamp])
                    print("-----------------------------------------------------")
                    print('Total Appearance Time: ', appearance_time)
                    print("-----------------------------------------------------")

                try:
                    frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # resize frame (optional)
                except Exception as e:
                    print("resize error:" + str(e))
                    break;
                # frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # resize frame (optional)

                curTime = time.time() + 1  # calc fps
                timeF = frame_interval

                if c % timeF == 0:
                    # new
                    timestamp = round(video_capture.get(cv2.CAP_PROP_POS_MSEC) / 1000, 2)
                    find_results = []
                    if frame.ndim == 2:
                        frame = to_rgb(frame)
                    frame = frame[:, :, 0:3]
                    bounding_boxes, _ = detect_face(frame, minsize, pnet, rnet, onet, threshold, factor)
                    nrof_faces = bounding_boxes.shape[0]
                    print('Detected_FaceNum: %d' % nrof_faces)

                    if nrof_faces > 0:
                        det = bounding_boxes[:, 0:4]
                        img_size = np.asarray(frame.shape)[0:2]

                        cropped = []
                        scaled = []
                        scaled_reshape = []
                        bb = np.zeros((nrof_faces, 4), dtype=np.int32)

                        for i in range(nrof_faces):
                            emb_array = np.zeros((1, embedding_size))

                            bb[i][0] = det[i][0]
                            bb[i][1] = det[i][1]
                            bb[i][2] = det[i][2]
                            bb[i][3] = det[i][3]

                            # inner exception
                            if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
                                print('Face is very close!')
                                continue

                            cropped.append(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
                            if i >= len(cropped):
                                break
                            cropped[i] = flip(cropped[i], False)
                            scaled.append(misc.imresize(cropped[i], (image_size, image_size), interp='bilinear'))
                            scaled[i] = cv2.resize(scaled[i], (input_image_size, input_image_size),
                                                   interpolation=cv2.INTER_CUBIC)
                            scaled[i] = prewhiten(scaled[i])
                            scaled_reshape.append(scaled[i].reshape(-1, input_image_size, input_image_size, 3))
                            feed_dict = {images_placeholder: scaled_reshape[i], phase_train_placeholder: False}
                            emb_array[0, :] = sess.run(embeddings, feed_dict=feed_dict)
                            predictions = model.predict_proba(emb_array)
                            print(predictions)
                            best_class_indices = np.argmax(predictions, axis=1)
                            best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
                            # print("predictions")
                            print(HumanNames[best_class_indices[0]], ' with accuracy ', best_class_probabilities)

                            # print(best_class_probabilities)
                            if best_class_probabilities > 0.56 and HumanNames[best_class_indices[0] == target_name]:
                                # new
                                if not last_appearance:
                                    start_time = timestamp
                                    last_appearance = True
                                # cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0),
                                #               2)  # boxing face

                                # plot result idx under box
                                text_x = bb[i][0]
                                text_y = bb[i][3] + 20
                                print('Result Indices: ', best_class_indices[0])
                                print(HumanNames)
                                for H_i in HumanNames:
                                    if HumanNames[best_class_indices[0]] == H_i:
                                        result_names = HumanNames[best_class_indices[0]]
                                        print(result_names)
                                        # cv2.putText(frame, result_names, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL,
                                        #             1, (0, 0, 255), thickness=1, lineType=2)
                            # new
                            else:
                                if last_appearance:
                                    end_time = timestamp
                                    last_appearance = False
                                    last_last_appearance = True
                                # 如果连续两次人脸识别失败，则判定人脸持续时间结束
                                elif last_last_appearance:
                                    appearnace = {}
                                    appearnace["target_name"] = result_names
                                    appearnace["start_time"] = start_time
                                    appearnace["end_time"] = end_time
                                    result['appearance_time'].append(appearnace)
                                    appearance_time.append([start_time, end_time])
                                    last_last_appearance = False
                    else:
                        # new
                        if last_appearance:
                            end_time = timestamp
                            last_appearance = False
                            last_last_appearance = True
                        # 如果连续两次人脸识别失败，则判定人脸持续时间结束
                        elif last_last_appearance:
                            appearnace = {}
                            appearnace["target_name"] = result_names
                            appearnace["start_time"] = start_time
                            appearnace["end_time"] = end_time
                            result['appearance_time'].append(appearnace)
                            appearance_time.append([start_time, end_time])
                            last_last_appearance = False
                        print('Alignment Failure')
                    # new
                    print('Timestamp: ', timestamp)
                    print('Appearance Time: ', appearance_time)
                    print('result', result)

                # c+=1
                # cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            video_capture.release()
            # cv2.destroyAllWindows()
            return json.dumps(result)
