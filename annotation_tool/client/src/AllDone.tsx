import React from 'react';
import './index.css';
import { CloseOutlined } from '@ant-design/icons';
import { SmileOutlined } from '@ant-design/icons';
import { Button, Result } from 'antd';



const AllDone: React.FC = () => {

    return (
        <Result
            icon={<SmileOutlined/>}
            title="All tasks are done!"
            subTitle="Thanks again for your contribution to our experiential study."
            extra={<Button type="primary">Please Close This Page</Button>}
        />
    );
};

export default AllDone;
