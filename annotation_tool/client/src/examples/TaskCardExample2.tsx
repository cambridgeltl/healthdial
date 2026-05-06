import React, {useState} from 'react';
import {Row, Col, Card, Input, Steps, message, theme, Button, Result} from 'antd';

import {SmileOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
const { TextArea } = Input;

interface TaskCardProps {
    style?: React.CSSProperties;  // Optional style prop
}


const TaskCardExample2: React.FC<TaskCardProps> = ({ style }) => {

    const [messageApi, contextHolder] = message.useMessage();
    const [current, setCurrent] = useState(2);
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

    const step_items = [{ key: "Step 1", title: "Step 1" }, { key: "Step 2", title: "Step 2" }, { key: "Step 3", title: "Done" }]

    return (
        <div>
            {contextHolder}
            <Card size="small"
                  hoverable={true}
                  style={style}>
                <Steps current={current} items={step_items} />
                <div style={contentStyle}>

                    <Result
                        icon={<SmileOutlined />}
                        title="Great, we have completed this card!"
                        // extra={<Button type="primary">Next</Button>}
                    />
                </div>
                <div style={{ marginTop: 24 }}>

                    <Button style={{ margin: '0 8px' }}>
                        Previous
                    </Button>
                </div>
            </Card>
        </div>

    );
};

export default TaskCardExample2;
