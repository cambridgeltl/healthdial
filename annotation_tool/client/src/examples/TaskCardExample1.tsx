import React, {useState} from 'react';
import {Row, Col, Card, Input, Steps, message, theme, Button, Result, Tooltip} from 'antd';

import {SmileOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import goodMorningAudio from "../media/good_morning.wav";
const { TextArea } = Input;

interface TaskCardProps {
    style?: React.CSSProperties;  // Optional style prop
}


const TaskCardExample1: React.FC<TaskCardProps> = ({ style }) => {

    const audioUrl = goodMorningAudio;
    const [messageApi, contextHolder] = message.useMessage();
    const [current, setCurrent] = useState(1);
    const { token } = theme.useToken();

    const contentStyle: React.CSSProperties = {
        height: 200,
        textAlign: 'center',
        display: 'flex',         // Set display to flex
        justifyContent: 'center', // Center horizontally
        alignItems: 'center',     // Center vertically
        color: token.colorTextTertiary,
        backgroundColor: token.colorFillAlter,
        borderRadius: token.borderRadiusLG,
        border: `1px dashed ${token.colorBorder}`,
        marginTop: 16,
    };

    const next = () => {
        if(audioUrl){
            setCurrent(current + 1);
        } else {
            messageApi.open({
                type: 'error',
                content: 'Please record audio before proceeding.',
                duration: 10,
            });
        }
    };

    const prev = () => {
        setCurrent(current - 1);
    };


    const step_items = [{ key: "Step 1", title: "Step 1" }, { key: "Step 2", title: "Step 2" }, { key: "Step 3", title: "Done" }]

    return (
        <div>
            {contextHolder}
            {/**/}
            <Tooltip title="Using the given prompt, you may create the following utterance." visible={true}  placement="right" >
            <Card size="small"
                  hoverable={true}
                  style={style}>
                <Steps current={current} items={step_items} />
                <div style={contentStyle}>
                        <div>
                            {audioUrl ? (
                                <div>
                                    <audio src={audioUrl} controls />

                                    <p>Please transcribe the audio:</p>
                                    <Row>
                                        <Col span={24}>
                                            <TextArea value={"Good morning, could you tell me more about traditional medicine?"} rows={2} style={{ width: '100%' }} />
                                        </Col>
                                    </Row>

                                </div>
                            ) : (
                                <p>Could you go to the previous step and try again?</p>
                            )}
                        </div>
                    <div>
                    </div>
                </div>
                <div style={{ marginTop: 24 }}>
                        <Button type="primary"
                        disabled={!audioUrl}>
                            Next
                        </Button>


                        <Button style={{ margin: '0 8px' }}>
                            Previous
                        </Button>
                </div>
            </Card>
            </Tooltip>

        </div>

    );
};

export default TaskCardExample1;
