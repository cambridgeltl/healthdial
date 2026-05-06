import React, {useState} from 'react';
import {Card} from 'antd';
import {List } from 'antd';

import {KnowledgeSnippetType} from './types/taskTypes';




interface KnowledgeSnippetListProps {
    snippet_list: KnowledgeSnippetType[];
}

interface TextContentProps {
    content: string;
}

const TextContentReact: React.FC<TextContentProps> = ({ content }) => {
    const formattedContent = content.split('\n').map((line, index) => {
        if (line.includes('*')) {
            return <li key={index}>{line.replace('* ', '* ')}</li>; // replace '* ' with an empty string
        }
        return <p key={index}>{line}</p>;
    });

    return (
        <div>
            {formattedContent}
        </div>
    );
};



const KnowledgeSnippetList: React.FC<KnowledgeSnippetListProps> = ({snippet_list}) => {

    return (
        <div>
            <Card
                size="small"
                  // style={{ width: 800 }}
                  // title="Knowledge Snippets"
                  hoverable={true}>
                <List
                    itemLayout="vertical"
                    size="large"
                    // grid={{ gutter: 16, column: 2 }}
                    style={ {
                        maxHeight: '400px', // Adjust this value based on your needs
                        overflowY: 'auto'
                    }}
                    dataSource={snippet_list}
                    renderItem={(item) => (
                        <List.Item
                            key={item.unique_identifier}
                        >
                            <List.Item.Meta
                                // title={<a href={item.url}>{item.data.title}</a>}
                                title={item.data.title}
                                description={item.data.topic}
                            />
                            <TextContentReact content={item.data.content} />


                        </List.Item>
                    )}
                />
            </Card>



        </div>

    );
};

export default KnowledgeSnippetList;
