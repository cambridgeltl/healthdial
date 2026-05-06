import React, { useEffect, useState } from 'react';
import {
    Row,
    Col,
    Card,
    Input,
    Steps,
    message,
    theme,
    Button,
    Result,
    Select,
    Layout,
    Collapse,
    Avatar,
} from 'antd';

import {SmileOutlined, UserOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import Cookies from "js-cookie";
import {contact_address, contact_email, contact_name, experiment_title, target_language, user_colour} from "./configs";
import UserTurn from "./UserTurn";
import SystemTurn from "./SystemTurn";
import {useNavigate} from "react-router-dom";
const {Header, Content, Footer} = Layout;
const { Option } = Select;


const DEVICE_COOKIE_NAME = 'selectedAudioDeviceId';

const AudioCheck: React.FC = () => {

    const [audioUrl, setAudioUrl] = useState<string | null>(null);

    const [messageApi, contextHolder] = message.useMessage();
    const [current, setCurrent] = useState(0);
    const { token } = theme.useToken();
    const [devices, setDevices] = useState<MediaDeviceInfo[]>([]);
    const [selectedDeviceId, setSelectedDeviceId] = useState<string | undefined>(undefined);

    const navigate = useNavigate();

    useEffect(() => {

        const fetchDevices = async () => {
            try {
                const deviceInfos = await navigator.mediaDevices.enumerateDevices();
                const audioDevices = deviceInfos.filter(device => device.kind === 'audioinput');
                setDevices(audioDevices);

                console.log('Available audio devices:', audioDevices);


                const savedDeviceId = Cookies.get(DEVICE_COOKIE_NAME);

                console.log('Saved audio device ID:', savedDeviceId)

                if (savedDeviceId) {
                    const savedDeviceExists = audioDevices.some(device => device.deviceId === savedDeviceId);
                    if (savedDeviceExists) {
                        setSelectedDeviceId(savedDeviceId);
                    } else {
                        message.error('Saved audio device not found. Please select another microphone.');
                        Cookies.remove(DEVICE_COOKIE_NAME);
                    }
                } else if (audioDevices.length > 0) {
                    setSelectedDeviceId(audioDevices[0].deviceId);
                }

            } catch (error) {
                console.error('Error accessing media devices:', error);
            }
        };

        fetchDevices();
    }, []);

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


    const handleDeviceChange = (value: string) => {
        setSelectedDeviceId(value);
        Cookies.set(DEVICE_COOKIE_NAME, value, { expires: 365 }); // Save deviceId to cookies for 1 year

        console.log(`Selected device: ${value}`);
    };

    const next = async () => {
        setCurrent(current + 1);
    };

    const prev = () => {
        setCurrent(current - 1);
    };


    const step_items = [
        { key: "Step 1", title: "Microphone Setup" },
        { key: "Step 2", title: "Recording Quality Check" },
        { key: "Step 3", title: "Done" }
    ];

    const addAudioElement = (blob: Blob) => {
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
    };

    const warningAudioPermission = () => {
        messageApi.open({
            type: 'error',
            content: 'Please allow microphone access to record audio.',
            duration: 10,
        });
    };

    return (


        <Layout>
            <Header
                style={{
                    backgroundColor: '#F5F5F5FF',
                    padding: 0,
                }}
            >
                <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                    <b>
                        {experiment_title}
                    </b>
                </div>

            </Header>

            <Content className="site-layout">
                <div>
                    <Collapse defaultActiveKey={['1', '2']}>

                        <Collapse.Panel header="Contact" key="1">
                            <p style={{"fontSize": 15, 'whiteSpace': 'pre-line'}}>
                                {contact_name}
                                <br/>
                                {contact_address}
                                <br/>
                                {contact_email}
                            </p>
                        </Collapse.Panel>

                        <Collapse.Panel header="Microphone Setup" key="2">
                            <div>
                                {contextHolder}
                                <Card size="small"
                                      hoverable={true}
                                >
                                    <Steps current={current} items={step_items} />


                                    <div style={contentStyle}>
                                        {current === 0 && (
                                            <div>

                                                <Select
                                                    value={selectedDeviceId}
                                                    onChange={handleDeviceChange}
                                                    style={{ width: '100%' }}
                                                    placeholder="Select a microphone"
                                                >
                                                    {devices.map(device => (
                                                        <Option key={device.deviceId} value={device.deviceId}>
                                                            {device.label || `Microphone ${device.deviceId}`}
                                                        </Option>
                                                    ))}
                                                </Select>
                                                {selectedDeviceId && (
                                                    <p style={{ marginTop: '1rem' }}>
                                                        Current microphone: {devices.find(device => device.deviceId === selectedDeviceId)?.label || 'Unknown'}
                                                    </p>
                                                )}
                                            </div>
                                        )


                                        }
                                        {current === 1 && (


                                            <div>
                                                {!audioUrl ? (

                                                    <div>
                                                        <Row>
                                                            <p>Please read the following text to check the quality of your microphone recording.</p>
                                                            <Input value={"Good morning, could you tell me more about traditional medicine?"} />
                                                        </Row>

                                                        <Row justify="center" style={{marginTop: '20px'}}>
                                                            <Col>
                                                                <AudioRecorder
                                                                    onRecordingComplete={addAudioElement}
                                                                    audioTrackConstraints={{
                                                                        deviceId: selectedDeviceId ? {exact: selectedDeviceId} : undefined,
                                                                        noiseSuppression: true,
                                                                        echoCancellation: true,
                                                                    }}
                                                                    downloadFileExtension="webm"
                                                                    mediaRecorderOptions={{
                                                                        audioBitsPerSecond: 128000,
                                                                    }}
                                                                    showVisualizer={true}
                                                                    onNotAllowedOrFound={warningAudioPermission}
                                                                    classes={{
                                                                        AudioRecorderDiscardClass: 'start-save-audio',
                                                                        AudioRecorderStartSaveClass: 'start-save-audio',
                                                                    }}/>
                                                            </Col>
                                                        </Row>
                                                    </div>
                                                ) : (
                                                    <div>
                                                        <Row justify="center" align="middle" >
                                                            <p>
                                                                Listen the recorded audio. Can you hear your voice clearly? If you are satisfied with the quality, click Next. '
                                                            </p>
                                                            <p>
                                                                Otherwise, you can re-record the audio by clicking the 'Re-record' button. You may change your recording device and environment if needed.
                                                            </p>
                                                            {/*<Input value={"Good morning, could you tell me more about traditional medicine?"} />*/}
                                                        </Row>
                                                        <Row justify="center" align="middle" style={{ marginTop: '20px' }}>

                                                            <Col><audio src={audioUrl} controls /></Col><Col>
                                                            <Button style={{ marginLeft: '10px' }} onClick={() => setAudioUrl(null)}>
                                                                Re-record
                                                            </Button>
                                                        </Col>
                                                        </Row>
                                                    </div>
                                                )}

                                            </div>





                                        )}
                                        {current === 2 && (
                                            <div>
                                                <Result
                                                    icon={<SmileOutlined />}
                                                    title="Great, we have completed this test! Now, you can proceed to the data collection task."
                                                />
                                            </div>
                                        )}

                                    </div>

                                    <div style={{ marginTop: 24 }}>
                                        {current < step_items.length - 1 && (
                                            <Button type="primary"
                                                    disabled={current === 1 && !audioUrl}
                                                    onClick={() => next()}>
                                                Next
                                            </Button>
                                        )}

                                        {current > 0 && current < 2 && (
                                            <Button style={{ margin: '0 8px' }} onClick={() => prev()}>
                                                Previous
                                            </Button>
                                        )}

                                        {current === 2 && (
                                            <Button type="primary"
                                                // disabled={current === 1 && !audioUrl}
                                                    onClick={() =>  navigate('/assignment')}>
                                                Finish
                                            </Button>
                                        )}
                                    </div>
                                </Card>
                            </div>
                        </Collapse.Panel>
                    </Collapse>
                </div>

            </Content>
            <Footer style={{textAlign: 'center', backgroundColor: '#F5F5F5FF'}}>Cambridge LTL ©2024</Footer>
        </Layout>


    );
};

export default AudioCheck;
