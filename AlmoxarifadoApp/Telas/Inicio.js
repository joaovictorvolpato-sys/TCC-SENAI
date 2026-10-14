import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  Image,
  Modal,
  ScrollView,
  StyleSheet,
  StatusBar,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { API_URL } from '../config';

export default function Inicio({ navigation }) {
  const [itens, setItens] = useState([]);
  const [fotoAberta, setFotoAberta] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 8000);

    async function carregar() {
      try {
        const resposta = await fetch(API_URL + '/api/itens', {
          signal: controller.signal,
        });
        if (!resposta.ok) throw new Error('HTTP ' + resposta.status);
        setItens(await resposta.json());
      } catch (e) {
        console.log('Erro ao carregar itens:', e.message);
      } finally {
        clearTimeout(timer);
      }
    }

    carregar();
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, []);

  function mostrar_foto(caminho) {
    setFotoAberta(caminho);
  }

  const cards = [
    { titulo: 'Adicionar Estoque', texto: 'Inserir itens ao estoque.', tela: 'adicionar' },
    { titulo: 'Retirar Estoque', texto: 'Registrar saídas do estoque.', tela: 'Retirar' },
    { titulo: 'Cadastrar Usuario', texto: 'Cadastre um novo usuario.', tela: 'Usuarios' },
  ];

  return (
    <SafeAreaView style={styles.corpo}>
      <StatusBar barStyle="light-content" />
      <ScrollView>
        <View style={styles.cabecalho}>
          <Text style={styles.cabecalhoTitulo}>Sistema de Almoxarifado Senai</Text>
          <Text style={styles.cabecalhoTexto}>Controle de materiais e estoque</Text>
        </View>

        <View style={styles.secaoCards}>
          {cards.map((card) => (
            <View key={card.tela} style={styles.card}>
              <Text style={styles.cardTitulo}>{card.titulo}</Text>
              <Text style={styles.cardTexto}>{card.texto}</Text>
              <TouchableOpacity
                style={styles.btn}
                onPress={() => navigation.navigate(card.tela)}
              >
                <Text style={styles.btnTexto}>Acessar</Text>
              </TouchableOpacity>
            </View>
          ))}
        </View>

        <ScrollView horizontal style={styles.caixaTabela}>
          <View style={styles.tabela}>
            <View style={styles.linhaCabecalho}>
              <Text style={[styles.th, styles.colId]}>ID</Text>
              <Text style={[styles.th, styles.colNome]}>Nome</Text>
              <Text style={[styles.th, styles.colCategoria]}>Categoria</Text>
              <Text style={[styles.th, styles.colFuncao]}>Funcao</Text>
              <Text style={[styles.th, styles.colQtd]}>Quantidade</Text>
              <Text style={[styles.th, styles.colValor]}>Valor</Text>
              <Text style={[styles.th, styles.colFoto]}>Foto</Text>
            </View>

            {itens.map((item) => (
              <View key={String(item.id)} style={styles.linha}>
                <Text style={[styles.thLinha, styles.colId]}>{item.id}</Text>
                <Text style={[styles.td, styles.colNome]}>{item.nome}</Text>
                <Text style={[styles.td, styles.colCategoria]}>{item.categoria}</Text>
                <Text style={[styles.td, styles.colFuncao]}>{item.funcao}</Text>
                <Text style={[styles.td, styles.colQtd]}>{item.quantidade}</Text>
                <Text style={[styles.td, styles.colValor]}>{item.valor}</Text>
                <View style={[styles.td, styles.colFoto]}>
                  {item.foto ? (
                    <TouchableOpacity
                      style={styles.btnFoto}
                      onPress={() => mostrar_foto(API_URL + '/static/' + item.foto)}
                    >
                      <Text style={styles.btnFotoTexto}>Foto</Text>
                    </TouchableOpacity>
                  ) : (
                    <Text>Sem foto</Text>
                  )}
                </View>
              </View>
            ))}
          </View>
        </ScrollView>
      </ScrollView>

      <Modal
        visible={fotoAberta !== null}
        transparent
        animationType="fade"
        onRequestClose={() => setFotoAberta(null)}
      >
        <View style={styles.modalFundo}>
          <View style={styles.modalCaixa}>
            {fotoAberta && (
              <Image
                source={{ uri: fotoAberta }}
                style={styles.modalImagem}
                resizeMode="contain"
              />
            )}
            <TouchableOpacity style={styles.btn} onPress={() => setFotoAberta(null)}>
              <Text style={styles.btnTexto}>OK</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const AZUL = '#005583';

const styles = StyleSheet.create({
  corpo: { flex: 1, backgroundColor: '#F4F4F4' },
  cabecalho: {
    backgroundColor: AZUL,
    paddingVertical: 30,
    paddingHorizontal: 16,
    alignItems: 'center',
  },
  cabecalhoTitulo: { color: '#FFFFFF', fontSize: 24, fontWeight: 'bold', textAlign: 'center' },
  cabecalhoTexto: { color: '#FFFFFF', fontSize: 14, marginTop: 10 },
  secaoCards: { padding: 20, alignItems: 'center' },
  card: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    paddingVertical: 28,
    paddingHorizontal: 16,
    alignItems: 'center',
    marginBottom: 16,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 6,
    shadowOffset: { width: 0, height: 2 },
    elevation: 3,
  },
  cardTitulo: { color: '#003F73', fontSize: 22, fontWeight: 'bold', marginBottom: 12 },
  cardTexto: { color: '#555555', fontSize: 15, marginBottom: 24 },
  btn: {
    backgroundColor: AZUL,
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 4,
  },
  btnTexto: { color: '#FFFFFF', fontSize: 16 },
  caixaTabela: { marginHorizontal: 10, marginBottom: 30 },
  tabela: { borderWidth: 1, borderColor: AZUL, backgroundColor: '#FFFFFF' },
  linhaCabecalho: { flexDirection: 'row', backgroundColor: AZUL },
  linha: { flexDirection: 'row', borderTopWidth: 1, borderTopColor: AZUL },
  th: { color: '#FFFFFF', fontWeight: 'bold', fontSize: 15, padding: 10 },
  thLinha: {
    backgroundColor: AZUL,
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 15,
    padding: 10,
  },
  td: {
    color: '#000000',
    fontSize: 15,
    padding: 10,
    borderLeftWidth: 1,
    borderLeftColor: AZUL,
  },
  colId: { width: 60 },
  colNome: { width: 120 },
  colCategoria: { width: 130 },
  colFuncao: { width: 120 },
  colQtd: { width: 110 },
  colValor: { width: 90 },
  colFoto: { width: 100 },
  btnFoto: {
    borderWidth: 1,
    borderColor: '#767676',
    backgroundColor: '#EFEFEF',
    borderRadius: 3,
    paddingVertical: 2,
    paddingHorizontal: 8,
    alignSelf: 'flex-start',
  },
  btnFotoTexto: { fontSize: 13, color: '#000000' },
  modalFundo: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.5)',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  modalCaixa: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    padding: 20,
    alignItems: 'center',
  },
  modalImagem: { width: '100%', height: 300, marginBottom: 20 },
});