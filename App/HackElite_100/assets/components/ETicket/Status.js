import React from 'react';
import {
    SafeAreaView,
    StyleSheet,
    ScrollView,
    View,
    Text,
    StatusBar,
} from 'react-native';

const GLOBAL = require('../../GlobalConstants')

export default class Status extends React.Component {
    render() {
        return (
            <View style={{
                alignItems: "center",
                margin: 20
            }}>
                <Text>Your documents are being verified</Text>
                <View
                    style={{
                        height: 20,
                        width: "100%",
                        borderRadius: 10,
                        marginTop: 10,
                        borderWidth: 1,
                        borderColor: GLOBAL.COLOR.GRAY
                    }}
                >

                </View>
            </View>
        )
    }
}