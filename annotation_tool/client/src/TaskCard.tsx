import React, { useEffect, useState } from 'react';
import { Row, Col, Card, Input, Steps, message, theme, Button, Result, Form, Spin } from 'antd';
import Cookies from "js-cookie";

import { SmileOutlined } from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import getBlobDuration from "get-blob-duration";
import useToken from "./service/TokenService";
import {serverUrl, target_language} from './configs';
const { TextArea } = Input;

interface TaskCardProps {
    turn_id?: number;
    task_id?: string;
    style?: React.CSSProperties;
    form?: any;
    before_login?: boolean;

}

const DEVICE_COOKIE_NAME = 'selectedAudioDeviceId';


const sendAudioToAsrServer = async (blob: Blob | null, audioUrl: string, token: string | null, task_id: string | undefined, turn_id: number) => {
    const formData = new FormData()
    if (blob != null) {

        formData.append("audio", blob, String(task_id) + '_' + String(turn_id) + '.wav');
        console.log("asr_upload");
        console.log(formData);
        const response = await fetch(serverUrl+'/audio/asr', {
            method: 'POST',
            body: formData,
            headers: { 
                // 'Content-Type': 'multipart/form-data',
                'Authorization': 'Bearer ' + token
             }
        });
        const data = await response.json();
        console.log('asr_result')
        console.log(data.transcription)
        return data.transcription;
    }else{
        message.error('You need to at least record one audio');
        return null
    }

    // await new Promise(resolve => setTimeout(resolve, 1000));
    // return "This is the asr result...";
};


const sendAudioToAsrServer_before_login = async (blob: Blob | null, audioUrl: string, token: string | null, task_id: string | undefined, turn_id: number) => {
    const formData = new FormData()
    if (blob != null) {

        formData.append("audio", blob, String(task_id) + '_' + String(turn_id) + '.wav');
        console.log("asr_upload");
        console.log(formData);
        const response = await fetch(serverUrl+'/audio/asr_pre', {
            method: 'POST',
            body: formData,
            headers: {
                // 'Content-Type': 'multipart/form-data',
                // 'Authorization': 'Bearer ' + token
            }
        });
        const data = await response.json();
        console.log('asr_result')
        console.log(data.transcription)
        return data.transcription;
    }else{
        message.error('You need to at least record one audio');
        return null
    }

};

const saveAudioToServer = async (blob: Blob, transcription: string, asrResult: string, authToken: string | null, task_id: string | undefined, turn_id: number) => {
    const formData = new FormData();

    // const saved_data = {
    //     "transcription" : transcription,
    //     "asr_result" : asrResult,
    //     "audio" : blob,
    //     "task_id" : "task_id",
    //     "turn_id" : "turn_id",
    //     "language" : target_language
    // }

    if (blob != null) {

        formData.append("audio", blob, String(task_id) + '_' + String(turn_id) + '.wav');
        formData.append("transcription", transcription);
        formData.append("asr_result", asrResult);
        if (task_id !== undefined) {
            formData.append("task_id", task_id);
        }
        else {
            formData.append("task_id", "task_id");
        }
        formData.append("turn_id", String(turn_id));
        formData.append("language",target_language)
        console.log("asr_upload");
        console.log(formData);
        const response = await fetch(serverUrl+'/audio/save_single_asr', {
            method: 'POST',
            body: formData,
            headers: { 
                //'Content-Type': 'multipart/form-data',
                'Authorization': 'Bearer ' + authToken
             }
        });
        const data = await response.json();
        console.log('asr_result')
        console.log(data.result)
        return data.result;
    }else{
        message.error('You need to at least record one audio');
        return 'You need to at least record one audio'
    }

};



const TaskCard: React.FC<TaskCardProps> = ({ style,turn_id = -1, task_id, form, before_login = false}) => {

    const [audioUrl, setAudioUrl] = useState<string | null>(null);
    const [audioDuration, setAudioDuration] = useState<number | null>(null);

    const [messageApi, contextHolder] = message.useMessage();
    const [current, setCurrent] = useState(0);
    const { token } = theme.useToken();
    const { token: authToken, removeToken, setToken, getUserRole, getUserPermissions } = useToken();
    const [blobData, setBlobData] = useState<Blob | null>(null);
    const [transcription, setTranscription] = useState('Loading speech recognition result, please wait....');
    const [asrResult, setAsrResult] = useState("");
    const [loading, setLoading] = useState<boolean>(false);
    const [submitting, setSubmitting] = useState<boolean>(false);

    const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(undefined);


    const contentStyle: React.CSSProperties = {
        height: 200,
        textAlign: 'center',
        display: 'flex',         // Set display to flex
        justifyContent: 'center', // Center horizontally
        alignItems: 'center',     // Center vertically
        color: token.colorTextTertiary,
        // color: token.colorError,

        backgroundColor: token.colorFillAlter,
        // backgroundColor: token.colorErrorBgHover,
        borderRadius: token.borderRadiusLG,
        border: `1px dashed ${token.colorBorder}`,
        marginTop: 16,
    };



    // useEffect to load savedDeviceId from cookies and validate its availability
    useEffect(() => {
        const fetchDevices = async () => {
            const deviceInfos = await navigator.mediaDevices.enumerateDevices();
            const audioDevices = deviceInfos.filter(device => device.kind === 'audioinput');

            const savedDeviceId = Cookies.get(DEVICE_COOKIE_NAME);

            if (savedDeviceId) {
                const savedDeviceExists = audioDevices.some(device => device.deviceId === savedDeviceId);
                if (savedDeviceExists) {
                    setSelectedDeviceId(savedDeviceId);
                } else {
                    Cookies.remove(DEVICE_COOKIE_NAME);
                    setSelectedDeviceId(undefined);
                }
            }
        };

        fetchDevices();
    }, []); // Empty dependency array ensures this runs only once when the component mounts


    useEffect(() => {

        if (form && turn_id !== -1) {
            form.setFieldsValue({
                [`blobData_${turn_id}`]: blobData,
                [`transcription_${turn_id}`]: transcription,
                [`asrResult_${turn_id}`]: asrResult,
            });
        }
    }, [blobData, transcription, asrResult, form, turn_id]);


    const next = async () => {
        if (audioUrl) {
            console.log('audioDuration && audioDuration > 1 && audioDuration < 120', audioDuration && audioDuration > 1 && audioDuration < 120)

            if (audioDuration && audioDuration > 1 && audioDuration < 120) {
                if (current === 0) {
                    setLoading(true);
                    try {
                        setCurrent(current + 1);
                        setTranscription('Loading speech recognition result, please wait...')

                        console.log("Runing ASR")

                        if (before_login){
                            const asrResponse = await sendAudioToAsrServer_before_login(blobData, audioUrl, authToken,task_id, turn_id);
                            setTranscription(asrResponse);
                            setAsrResult(asrResponse);

                        }else{
                            const asrResponse = await sendAudioToAsrServer(blobData, audioUrl, authToken,task_id, turn_id);
                            setTranscription(asrResponse);
                            setAsrResult(asrResponse);
                        }



                    } catch (error) {
                        console.log("error")
                        console.log(error)

                        console.log("SET Transcription")
                        setTranscription("Failed to retrieve ASR result. Please write the transcription manually.");
                        // console.log("SET asr")

                        setAsrResult("Failed to retrieve ASR result. Please write the transcription manually.");

                        messageApi.open({
                            type: 'error',
                            content: 'Failed to retrieve ASR result. Please try again.',
                            duration: 10,
                        });
                    } finally {
                        setLoading(false);
                    }



                } else if (current === 1) {

                    if (!form) {
                        console.log("Example model");
                        setCurrent(current + 1);
                        return;
                    }

                    if (blobData) {

                        if (before_login){
                            setCurrent(current + 1);
                        }else{

                            setSubmitting(true);

                            try {
                                const data = await saveAudioToServer(blobData, transcription, asrResult, authToken,task_id,turn_id);
                                console.log(data);
                                setCurrent(current + 1);
                            } catch (error) {
                                messageApi.open({
                                    type: 'error',
                                    content: 'Failed to save audio to server. Please try again.',
                                    duration: 10,
                                });
                            } finally {
                                setSubmitting(false);
                            }
                        }
                    } else {
                        messageApi.open({
                            type: 'error',
                            content: 'Audio data is missing. Please record again.',
                            duration: 10,
                        });
                    }


                } else {


                    setCurrent(current + 1);
                }

            } else {
                messageApi.open({
                    type: 'error',
                    content: 'Please record audio with a duration between 1 and 120 seconds before proceeding.',
                    duration: 10,
                });
            }

        } else {
            messageApi.open({
                type: 'error',
                content: 'Please record audio with a duration between 1 and 120 seconds before proceeding.',
                duration: 10,
            });
        }
    };

    const prev = () => {
        setCurrent(current - 1);
    };


    const step_items = [{ key: "Step 1", title: "Step 1" }, { key: "Step 2", title: "Step 2" }, { key: "Step 3", title: "Done" }]

    const addAudioElement = (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setBlobData(blob);

        getBlobDuration(blob).then(function (duration) {
            console.log(duration + ' seconds');
            setAudioDuration(duration);
        });


    };

    const warningAudioPermission = () => {
        messageApi.open({
            type: 'error',
            content: 'Please allow microphone access to record audio.',
            duration: 10,
        });
    };

    // const validateAsrResult = (_: any, value: any) => {
    //     if (!value) {
    //         // messageApi.open({
    //         //     type: 'error',
    //         //     content: 'No Asr data.',
    //         //     duration: 10,
    //         // });
    //         return Promise.reject(new Error('ASR result should not be empty.'));
    //     }
    //     // Add other validation logic here if needed
    //     return Promise.resolve();
    // };
    //
    // const validateBlobData = (_: any, value: any) => {
    //     if (!value) {
    //         messageApi.open({
    //             type: 'error',
    //             content: 'No audio data.',
    //             duration: 10,
    //         });
    //         return Promise.reject(new Error('Audio data is missing.'));
    //     }
    //     // Add other validation logic here if needed
    //     return Promise.resolve();
    // };



    const validateData = (_: any, value: any) => {

        // if (!asrResult){
        //     return Promise.reject(new Error('Please redo this utterance again.'));
        // }

        if (!value || !blobData) {
            return Promise.reject(new Error('Please complete this utterance.'));
        }

        if (current === 0 || current === 1) {
            return Promise.reject(new Error('Please click next before proceed.'));
        }

        // Add other validation logic here if needed
        return Promise.resolve();
    };

    return (
        <div>
            {contextHolder}
            <Card size="small"
                hoverable={true}
                style={style}
            >
                <Steps current={current} items={step_items} />


                <Form.Item
                    name={[`transcription_${turn_id}`]}
                    // rules={[{ required: true, message: 'Please answer this question.' }]}
                    rules={[{ validator: validateData }]}

                >
                    <Spin tip="Submitting..." spinning={submitting}>

                    <div style={contentStyle}>

                    {/*<Form.Item*/}
                    {/*    name={[`transcription_${turn_id}`]}*/}
                    {/*    // rules={[{ required: true, message: 'Please answer this question.' }]}*/}
                    {/*    rules={[{ validator: validateData }]}*/}

                    {/*>*/}
                        {/*{task_id} + {turn_id}*/}
                        {current === 0 && (
                            <AudioRecorder
                                onRecordingComplete={addAudioElement}
                                audioTrackConstraints={{
                                    deviceId: selectedDeviceId ? { exact: selectedDeviceId } : undefined,
                                    noiseSuppression: true,
                                    echoCancellation: true,
                                }}
                                // downloadOnSavePress={true}
                                downloadFileExtension="webm"
                                mediaRecorderOptions={{
                                    audioBitsPerSecond: 128000,
                                }}
                                showVisualizer={true}
                                onNotAllowedOrFound={warningAudioPermission}
                                classes={{
                                    AudioRecorderDiscardClass: 'start-save-audio',
                                    AudioRecorderStartSaveClass: 'start-save-audio',
                                }}
                            />
                        )}
                        {current === 1 && (
                            <div>
                                {audioUrl ? (
                                    <div>
                                        {/*This is {audioDuration} seconds long.*/}

                                        <audio src={audioUrl}
                                            controls
                                        />

                                    <p>Please transcribe the audio:</p>

                                        <Row>
                                            <Col span={24}>
                                                <Spin tip="Loading..." spinning={loading}>
                                                    {/*<Form.Item*/}
                                                    {/*    name={[turn_id, "transcription"]}*/}
                                                    {/*    rules={[{ required: true, message: 'Please transcribe the audio.' }]}*/}
                                                    {/*>*/}
                                                    <TextArea
                                                        rows={2}
                                                        style={{ width: '100%' }}
                                                        value={transcription}
                                                        onChange={(e) => setTranscription(e.target.value)}
                                                    />
                                                    {/*</Form.Item>*/}
                                                </Spin>
                                            </Col>
                                        </Row>
                                </div>
                            ) : (
                                <p>Could you go to the previous step and try again?</p>
                            )}
                        </div>
                    )}
                    {current === 2 && (
                        <div>
                            <Result
                                icon={<SmileOutlined />}
                                title="Great, we have completed this card!"
                            />
                        </div>
                    )}

                </div>
                    </Spin>
                </Form.Item>


                <div>
                    {/*style={{ height: '200px', width: '200px', overflow: 'hidden' }}*/}
                    <Form.Item
                        name={[`asrResult_${turn_id}`]}
                        // rules={[{ required: true, message: 'ASR result should not be empty.' }]}
                        // rules={[{ validator: validateAsrResult }]}

                        hidden={true}
                    >
                    </Form.Item>
                    <Form.Item
                        name={[`blobData_${turn_id}`]}
                        // rules={[{ required: true, message: 'Audio data is missing.' }]}
                        // rules={[{ validator: validateBlobData }]}

                        hidden={true}

                    >
                    </Form.Item>
                </div>
                <div style={{ marginTop: 24 }}>
                    {current < step_items.length - 1 && (
                        <Button type="primary"
                            disabled={!audioUrl || loading || submitting}
                            onClick={() => next()}>
                            Next
                        </Button>
                    )}

                    {current > 0 && (
                        <Button style={{ margin: '0 8px' }} onClick={() => prev()}>
                            Previous
                        </Button>
                    )}
                </div>
            </Card>
        </div>

    );
};

export default TaskCard;
