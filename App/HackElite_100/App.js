import React, { lazy } from 'react';
import {
  SafeAreaView,
  StyleSheet,
  ScrollView,
  View,
  Text,
  StatusBar,
  Image
} from 'react-native';

import LiveUpdatesScreen from './assets/screens/TabScreens/LiveUpdatesScreen'
import TransportationScreen from './assets/screens/TabScreens/TransportationScreen'
import ETicketScreen from './assets/screens/TabScreens/ETicketScreen'
import ProfileScreen from './assets/screens/TabScreens/ProfileScreen'


//import LiveUpdates from '../assets/images/live_updates.svg';
//import Transportation from '../assets/images/transportation.svg';
//import E_Ticket from '../assets/images/e_ticket.svg';
//import Profile from '../assets/images/profile.svg';

import HorribleEmoji from '../assets/images/profile.svg';



import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';



const GLOBAL = require('./assets/GlobalConstants')


import { createStackNavigator } from '@react-navigation/stack';


const AllStack = createStackNavigator();

function AllStackCall() {
  return (
    <AllStack.Navigator>
      <AllStack.Screen
        name="LiveUpdatesHome"
        component={MyTabs}
        options={{

        }}

      />

    </AllStack.Navigator>
  );
}


const BottomTabs = createBottomTabNavigator();
function MyTabs() {
  return (
    <BottomTabs.Navigator
      tabBarOptions={{
        activeTintColor: GLOBAL.COLOR.BLUE,

      }}
    >
      <BottomTabs.Screen
        name="Live Updates"
        component={LiveUpdatesScreen}      //pehle CommunityStackCall tha
        options={{
          tabBarLabel: 'Live Updates',
          tabBarIcon: ({ color, size }) => (
            <HorribleEmoji
              height={40}
              width={40}
            />
          ),
        }}
      />
      <BottomTabs.Screen
        name="Transportation"
        component={TransportationScreen}
        options={{
          tabBarLabel: 'Transportation',

        }}
      />
      <BottomTabs.Screen
        name="ETicket"
        component={ETicketScreen}
        options={{
          tabBarLabel: 'ETicket',

        }}
      />
      <BottomTabs.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarLabel: 'Profile',

        }}
      />
    </BottomTabs.Navigator>
  );
}

export default class App extends React.Component {
  render() {
    return (
      <View style={{ flex: 1 }}>
        <StatusBar backgroundColor={GLOBAL.COLOR.BLUE} />
        <NavigationContainer>
          <AllStackCall />
        </NavigationContainer>
      </View>
    )
  }
}