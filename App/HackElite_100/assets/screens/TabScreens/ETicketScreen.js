import React from 'react';
import {
    SafeAreaView,
    StyleSheet,
    ScrollView,
    View,
    Text,
    StatusBar,
    Image,
    TouchableOpacity

} from 'react-native';

import Status from '../../components/ETicket/Status'

const GLOBAL = require('../../GlobalConstants')



export default class ETicketScreen extends React.Component {
    render() {
        return (
            <View
                style={{
                    height: "100%",
                    width: "100%",

                }}
            >
                <Status />
                <View
                    style={{
                        flexDirection: "row",
                        height: "100%",
                        width: "100%",
                        justifyContent: "space-around"
                    }}
                >
                    <TouchableOpacity
                        onPress={() => {
                            //navigation.navigate('CreatePost')
                        }}
                        style={{
                            height: 180,
                            width: "40%",
                            backgroundColor: GLOBAL.COLOR.GRAY,
                            justifyContent: "center",
                            alignItems: "center"
                        }}
                    >

                        <Text>Application Form</Text>

                    </TouchableOpacity>

                    <TouchableOpacity
                        style={{
                            height: 180,
                            width: "40%",
                            backgroundColor: GLOBAL.COLOR.GRAY,
                            justifyContent: "center",
                            alignItems: "center"
                        }}
                    >

                        <Text>Medical Report</Text>

                    </TouchableOpacity>



                </View>
            </View>
        )
    }
}