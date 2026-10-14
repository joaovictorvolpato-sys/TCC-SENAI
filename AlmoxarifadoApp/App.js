import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
 
import Login from './Telas/Login';
import Inicio from './Telas/Inicio';
import Adicionar from './Telas/adicionar';

const Stack = createNativeStackNavigator();
 
export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator
        initialRouteName="Login"
        screenOptions={{ headerShown: false }}
      >
        <Stack.Screen name="Login" component={Login} />
        <Stack.Screen name="Inicial" component={Inicio} />
        <Stack.Screen name="adicionar" component={Adicionar} />
       
      </Stack.Navigator>
    </NavigationContainer>
  );
}
